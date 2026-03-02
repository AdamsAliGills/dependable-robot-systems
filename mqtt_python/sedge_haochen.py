#/***************************************************************************
#* Copyright (C) 2024 by DTU
#* Modified by Haochen (COG Method)
#***************************************************************************/

from datetime import *
import time as t
from threading import Thread
import cv2 as cv
import numpy as np
from ulog import flog

class SEdge_haochen:
    # raw AD values
    edge = [0, 0, 0 , 0, 0, 0, 0, 0]
    edgeUpdCnt = 0
    edgeTime = datetime.now()
    edgeInterval = 0
    # normalizing white values
    edge_n_w = [0, 0, 0 , 0, 0, 0, 0, 0]
    edge_n_wUpdCnt = 0
    edge_n_wTime = datetime.now()
    # normalized after white calibration
    edge_n = [0, 0, 0 , 0, 0, 0, 0, 0]
    edge_nUpdCnt = 0
    edge_nTime = datetime.now()
    edge_nInterval = 0
    edgeIntervalSetup = 0.1
    # line detection levels
    lineValidThreshold = 750 # 1000 is calibrated white
    crossingThreshold = 700 # average above this is assumed to be crossing line
    
    # line detection values
    posLeft = 0.0
    posRight = 0.0
    followLeft = True
    refPosition = 0.0 # distance from detected edge
    lineValid = False
    lineValidCnt = 0 # a value up to 20 for most confident line detect
    crossingLine = False
    crossingLineCnt = 0  # a value up to 20 for most confident crossing line
    average = 0
    high = 0 # highest reflectivity
    
    # management
    topicCmdT0 = ""
    sendCalibRequest = False
    
    # follow line controller
    lineCtrl = False 
    velocity = 0.0
    # Lead controller parameters
    lineKp = 1.0 
    lineTauZ = 0.8 
    lineTauP = 0.25 
    # Lead pre-calculated factors
    tauP2pT = 1.0
    tauP2mT = 0.0
    tauZ2pT = 1.0
    tauZ2mT = 0.0
    # control values
    lineE1 = 0.0 
    lineY1 = 0.0 
    lineY = 0.0  
    u = 0 

    def setup(self):
      from uservice import service
      sendBlack = False
      loops = 0
      print("% Edge (sedge.py):: turns on line sensor")
      self.topicCmdT0 = "robobot/cmd/T0"
      service.send(self.topicCmdT0, "lip 1")
      service.send(self.topicCmdT0,"sub livn 10")
      while not service.stop:
        t.sleep(0.02)
        if service.args.white:
          if not sendBlack:
            service.send(self.topicCmdT0, "litb 0 0 0 0 0 0 0 0")
            sendBlack = True
          elif self.edgeUpdCnt < 3:
            service.send(self.topicCmdT0,"livi")
          elif not self.sendCalibRequest:
            service.send(self.topicCmdT0,"liwi")
            t.sleep(0.02)
            service.send(self.topicCmdT0,"licw 100")
            print("# Edge (sedge.py):: sending calibration request")
            t.sleep(0.25)
            service.send(self.topicCmdT0,"eew")
            self.sendCalibRequest = True
            service.send(self.topicCmdT0,"liwi")
          else:
            t.sleep(0.25)
            service.args.white = False
            print(f"% Edge (sedge.py):: calibration finished.")
            service.stop = True
        elif self.edge_n_wUpdCnt == 0:
          service.send(self.topicCmdT0,"liwi")
        elif self.edge_nUpdCnt == 0:
          pass
        else:
          print(f"% Edge (sedge.py):: got data stream; after {loops} loops")
          break
        loops += 1
        if loops > 30:
          break

    def decode(self, topic, msg):
        used = True
        if topic == "T0/liv": 
          gg = msg.split(" ")
          if (len(gg) >= 4):
            t0 = self.edgeTime
            self.edgeTime = datetime.fromtimestamp(float(gg[0]))
            for i in range(8):
                self.edge[i] = int(gg[i+1])
            t1 = self.edgeTime
            dt = (t1 - t0).total_seconds() * 1000
            if self.edgeUpdCnt == 2:
              self.edgeInterval = dt
            elif self.edgeUpdCnt > 2:
              self.edgeInterval = (self.edgeInterval * 99 + dt) / 100
            self.edgeUpdCnt += 1
        elif topic == "T0/livn": 
          gg = msg.split(" ")
          if (len(gg) >= 4):
            t0 = self.edge_nTime
            self.edge_nTime = datetime.fromtimestamp(float(gg[0]))
            for i in range(8):
                self.edge_n[i] = int(gg[i+1])
            t1 = self.edge_nTime
            dt = (t1 - t0).total_seconds() * 1000
            if self.edge_nUpdCnt == 2:
              self.edge_nInterval = dt
            elif self.edge_nUpdCnt > 2:
              self.edge_nInterval = (self.edge_nInterval * 99 + dt) / 100
            self.edge_nUpdCnt += 1
            self.LineDetect()
            if self.lineCtrl:
              self.followLine()
            if self.edge_nUpdCnt % 10 == 0:
              flog.write()
        elif topic == "T0/liw": 
          gg = msg.split(" ")
          if (len(gg) >= 4):
            self.edge_n_wTime = datetime.fromtimestamp(float(gg[0]))
            for i in range(8):
                self.edge_n_w[i] = int(gg[i+1])
            self.edge_n_wUpdCnt += 1
        else:
          used = False
        return used

    def LineDetect(self):
        """
        Modified Line Detection using Center of Gravity (COG) method.
        """
        sum_val = 0
        high = 1
        # 1. Find the maximum brightness and average brightness
        for i in range(8):
            sum_val += self.edge_n[i]
            if self.edge_n[i] > high:
                high = self.edge_n[i]
        
        self.high = high
        self.average = sum_val / 8.0
        
        # 2. Determine if on the line and if it is a crossing line
        self.crossingLine = self.average >= self.crossingThreshold
        self.lineValid = self.high >= self.lineValidThreshold
        
        # 3. Calculate position using COG method
        if self.lineValid:
            cog_sum = 0
            pos_sum = 0
            # Exclude background noise, only calculate parts above the threshold
            low_limit = self.lineValidThreshold - 100
            
            for i in range(8):
                v = self.edge_n[i] - low_limit
                if v > 0:
                    cog_sum += v
                    # Map sensor indices to a range around center
                    pos_sum += (i + 1) * v
            
            if cog_sum > 0:
                # Map position to -3.5 to 3.5 range
                linePosition = (pos_sum / cog_sum) - 4.5
                self.posLeft = linePosition
                self.posRight = linePosition
        
        # 4. Update confidence counters
        if self.lineValid and self.lineValidCnt < 20:
            self.lineValidCnt += 1
        elif not self.lineValid:
            self.lineValidCnt = max(0, self.lineValidCnt - 1)
            
        if self.crossingLine and self.crossingLineCnt < 20:
            self.crossingLineCnt += 1
        elif not self.crossingLine:
            self.crossingLineCnt = max(0, self.crossingLineCnt - 1)

    def lineControl(self, velocity, followLeft = True, refPosition = 0):
      """
      Interface for mqtt-client.py to enable/disable line following.
      """
      self.velocity = velocity
      self.followLeft = followLeft
      self.refPosition = refPosition
      self.lineCtrl = velocity > 0.001
      pass

    def followLine(self):
      from uservice import service
      if abs(self.edge_nInterval - self.edgeIntervalSetup) > 2.0: 
        self.PIDrecalculate()
        self.edgeIntervalSetup = self.edge_nInterval
      
      # Using COG-based continuous position
      e = self.refPosition - self.posLeft
      
      # Calculate action (P-Lead controller)
      self.u = self.lineKp * e
      self.lineY = (self.u * self.tauZ2pT - self.lineE1 * self.tauZ2mT + self.lineY1 * self.tauP2mT)/self.tauP2pT
      
      if self.lineY > 4.0:
        self.lineY = 4.0
      elif self.lineY < -4.0:
        self.lineY = -4.0
        
      self.lineE1 = self.u
      self.lineY1 = self.lineY
      
      par = f"rc {self.velocity:.3f} {self.lineY:.3f} {t.time()}"
      service.send("robobot/cmd/ti", par)

    def PIDrecalculate(self):
      Tsec = self.edge_nInterval/1000
      self.tauP2pT = self.lineTauP * 2.0 + Tsec
      self.tauP2mT = self.lineTauP * 2.0 - Tsec
      self.tauZ2pT = self.lineTauZ * 2.0 + Tsec
      self.tauZ2mT = self.lineTauZ * 2.0 - Tsec

    def terminate(self):
      from uservice import service
      print("% Edge (sedge.py):: turn off line sensor")
      service.send(self.topicCmdT0, "lip 0")
      print("% Edge (sedge.py):: terminated")

    def paint(self, img):
      h, w, ch = img.shape
      pl = int(h - h/4) 
      st = int(w/10) 
      gh = int(h/2) 
      x = st 
      y = pl
      dtuGreen = (0x35, 0x88, 0)
      dtuBlue = (0xea, 0x3e, 0x2f)
      dtuRed = (0x00, 0x00, 0x99)
      dtuPurple = (0x8e, 0x23, 0x77)
      cv.line(img, (x,y), (int(x + 7*st), int(y)), dtuGreen, 1)
      cv.line(img, (x,int(y-gh)), (int(x + 7*st), int(y-gh)), dtuGreen, 1)
      cv.line(img, (x,int(y-gh*self.lineValidThreshold/1000.0)), (int(x + 7*st), int(y-gh*self.lineValidThreshold/1000.0)), dtuBlue, 1)
      for i in range(8):
        y_val = int(pl - self.edge_n[i]/1000 * gh)
        cv.drawMarker(img, (x,y_val), dtuRed, cv.MARKER_STAR, 2, 8, 10)
        x += st
      pixP = int((self.posLeft + 4.5)*st)
      cv.line(img, (pixP, int(pl)), (pixP, int(pl-gh)), dtuRed, 3)
      if self.crossingLine:
        cv.putText(img, "Crossing", (int(st),int(pl - 20)), cv.FONT_HERSHEY_PLAIN, 1, dtuRed, 2)

edge = SEdge_haochen()