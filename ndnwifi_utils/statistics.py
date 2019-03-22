# This work originally done by Xian Guo (iamxguo@aol.com), and
# modified by Nicholas Gordon (nmgordon@memphis.edu)

from abc import ABCMeta
import json
from copy import deepcopy
import re

class StatisticsFunctions(ABCMeta):

  def statisticData(self, consumerSet, dataFilePath):
    """Does statistical data extraction from nodes. This class is an
    interface for experiments, so it doesn't make much sense for it to
    be inherited by anything else.

    consumerSet: a set of consumers
    dataFilePath: a path used to save statistical data to"""
    consumerSTASet = []
    self.ensureDir(dataFilePath)

    # In the VNDN case, we need to additionally pick out the
    # car-stations and put them into the consumer group
    if self.isVndn or self.isSumoVndn:
      for consumer in consumerSet:
        for consumerSTA in self.carSTASet:
          carSTA = "car" + re.search('car(.+?)STA', str(consumerSTA)).group(1)
          if str(consumer) == carSTA:
            consumerSTASet.append(consumerSTA)

    # In the ordinary wifi case, we can directly use our list of nodes
    if self.isWiFi:
      if self.isVndn or self.isSumoVndn:
        self.extractData(self.net.carsSTA, consumerSTASet, dataFilePath, True)
        self.statisticResult(self.net.carsSTA, consumerSTASet, dataFilePath, True)
        self.extractData(self.net.cars, consumerSet, dataFilePath, False)
        self.statisticResult(self.net.cars, consumerSet, dataFilePath, False)
      # The simple case, we just have an ordinary wifi network with a topology of stations
      else:
        self.extractData(self.net.stations, consumerSet, dataFilePath, False)
        self.statisticResult(self.net.stations, consumerSet, dataFilePath, False)

    else:
      # This is the wired case, where we have hosts
      self.extractData(self.net.hosts, consumerSet, dataFilePath, False)
      self.statisticResult(self.net.hosts, consumerSet, dataFilePath, False)

  def extractData(self, nodeSet, consumerSet, dataFilePath, isCarSTA):
    """Uses a node's NFD log to extract raw data about network
    performance and write the extracted data to a file.

    nodeSet: a set of nodes in the network
    consumerSet: a set of consumer nodes int the network
    dataFilePath: a path used to save the experimental data
    isCarSTA: to distiguish between carx and carxSTA"""
    if isCarSTA:
      experimentData_file = open ("%s/experimentData-STA.dat" %dataFilePath, "w")
    else:
      experimentData_file = open ("%s/experimentData.dat" %dataFilePath, "w")

    # Load the existing JSON object array from the file into memory
    experimentDataJson = json.load(experimentData_file)

    # Extract some raw data from each node
    for sta in nodeSet:
        dataFile = "/tmp" + "/" +str(sta)+ "/" + "communicateData.dat"
        sta.cmd("cat {}.log | grep face={} > communicateData.dat".format(sta, self.wlanFaceId))
        input_file = open(dataFile, "r")
        needFirstOutgoingInterest = True
        needFirstIncomingData = True
        dataPoints = {'firstOutgoingInterestTime':None,
                      'firstIncomingDataTime':None}
        # Simple read loop
        for line in input_file:
          fields = line.split(" ")
          currentKey = fields[3].strip()
          if currentKey not in dataPoints:
            dataPoints[currentKey] = 0
          else:
            dataPoints[currentKey] = dataPoints[currentKey]+1
          # Extra processing for first-seen fields
          if currentKey == "onOutgoingInterest":
            if needFirstOutgoingInterest:
              dataPoints['firstOutgoingInterestTime'] = fields[0]
              needFirstOutgoingInterest = False
            elif currentKey == "onIncomingData":
              if needFirstIncomingData:
                dataPoints['firstIncomingDataTime'] = fields[0]
                needFirstIncomingData = False
        if sta in consumerSet: # The current node is a consumer
          dataPoints['nPings'] = self.nPings
        else: # The current node is not a consumer
          dataPoints['nPings'] = 0
        experimentDataJson.append(json.dumps(dataPoints))
        json.dump(experimentDataJson, experimentData_file)
        input_file.close()
        experimentData_file.close()

    # Generate the file used to save statistical data
    def statisticResult(self, nodeSet, consumerSet, dataFilePath, isCarSTA):
      """Read in statistical data extracted from a set of nodes and
      consumers to generate some network performance metrics.

      nodeSet: a set of nodes in the network
      consumerSet: a set of consumer nodes in the network
      dataFilePath: a path used to save the experimental data
      isCarSTA: this param is used for distiguishing is carx or carxSTA in VNDN or SUMOVNDN

      """
      nodeNumber = str(len(nodeSet))
      # need to modify the path for sotoring experimental data before doing experiment
      if isCarSTA:
        statResult_file = open("%s/statResult-STA-%s.dat" % (dataFilePath, nodeNumber), "a")
        input_file = open("%s/experimentData-STA.dat" % dataFilePath, "r")
      else:
        statResult_file = open ("%s/statResult-%s.dat" % (dataFilePath, nodeNumber), "a")
        input_file = open("%s/experimentData.dat" % dataFilePath, "r")

      dataPointsArray = json.load(input_file)

      results = deepcopy(dataPointsArray[0])
      # Explicit cast to float to avoid any dividing errors
      averageDelay = float(0)

      for individualResult in dataPointsArray[1:]:
        # We only want to consider the delay for consumers
        if individualResult['firstIncomingDataTime'] is not None \
           and individualResult['firstOutgoingInterestTime'] is not None \
           and individualResult['nPings'] != 0:
          averageDelay = averageDelay + \
                         (individualResult['firstIncomingDataTime'] - individualResult['firstOutgoingInterestTime']) / 2
        # Add each key-value pair from each individual result to the
        # overall result.
        for key in results.keys():
          # But we only want interest packets that consumers sent.
          if key == 'nPings' and results[key] == 0:
            pass
          results[key] += individualResult[key]

      if results['onOutgoingInterest'] != 0:
        interestLoss = abs(results['onOutgoingInterest'] - results['onIncomingInterest'])
        interestLossRate = float(interestLoss) / float(results['onOutgoingInterest'])
      if results['onOutgoingData'] != 0:
        dataLoss = abs(results['onOutgoingData'] - results['onIncomingData'])
        dataLossRate = float(dataLoss) / float(results['onOutgoingData'])

      if results['onOutgoingData'] != 0 and results['onOutgoingInterest'] != 0:
        packetLoss = abs((results['onOutgoingInterest'] + results['onOutgoingData']) - \
                         (results['onIncomingInterest'] + results['onIncomingData']))
        packetLossRate = float(packetLoss) / \
                         float(results['onOutgoingInterest'] + results['onOutgoingData'])
        json.dump(results, statResult_file)
        statResult_file.close()
        input_file.close()
