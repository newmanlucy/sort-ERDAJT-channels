import xml.etree.ElementTree as ET
import re
import ntpath
import argparse

def getChannelFromName(name):
    pattern = "Ch ([0-9]+).*"
    m = re.match(pattern, name)
    return int(m.group(1))


def convertChannel(controller, offset):
    if controller <= 50:
        return (controller - 1) * 16 + offset
    elif controller <= 59:
        return (16 * 49) + (controller - 50) * 24 + offset
    elif controller <= 64:
        return (16 * 49) + (24 * 9) + (controller - 59) * 16 + offset
    else:
        return (16 * 49)  + (24 * 9) + (16 * 5) + (controller - 64) * 24 + offset

def parseLMSfromXLights(filename):
    root = ET.parse(filename).getroot()
    channelEffectDict = {}
    for channel in root.findall('channels/channel'):
        channelName = channel.get("name")
        unit = channel.get("unit")
        circuit = channel.get("circuit")
        if unit is not None and circuit is not None:
           channelNum = convertChannel(int(unit), int(circuit))
        channelEffects = channel.findall("effect")
        channelEffectDict[channelNum] = channelEffects
    return root, channelEffectDict

def parseLMSfromLOR(filename):
    root = ET.parse(filename).getroot()
    channelDict = {}
    dummyList = []
    for channel in root.findall("channels/channel"):
        unit = channel.get("unit")
        circuit = channel.get("circuit")
        if circuit is not None and unit is not None:
            channelNum = convertChannel(int(unit), int(circuit))
            channelDict[channelNum] = channel
        else:
            name = channel.get("name")
            if name is not None:
                for effect in list(channel):
                    channel.remove(effect)
                dummyList.append(channel)
    return root, channelDict, dummyList

def newChannelFromOldChannel(oldChannel):
    newChannel = ET.Element("channel")
    newChannel.set("name", oldChannel.get("name"))
    newChannel.set("color", oldChannel.get("color"))
    newChannel.set("centiseconds", oldChannel.get("centiseconds"))
    newChannel.set("deviceType", oldChannel.get("deviceType"))
    newChannel.set("unit", oldChannel.get("unit"))
    newChannel.set("circuit", oldChannel.get("circuit"))
    newChannel.set("savedIndex", oldChannel.get("savedIndex"))
    return newChannel

def make_fifteen_two():
    # <channel name="Unit 15.02" color="12632256" centiseconds="18233" deviceType="LOR" unit="21" circuit="2" savedIndex="807"/>
    fifteen_two = ET.Element("channel")
    fifteen_two.set("name", "Unit 15.02")
    fifteen_two.set("color", "12632256")
    fifteen_two.set("centiseconds", "18233")
    fifteen_two.set("deviceType", "LOR")
    fifteen_two.set("unit", "21")
    fifteen_two.set("circuit", "2")
    fifteen_two.set("savedIndex", "807")
    return fifteen_two

def reconstructSequence(inputFile, orderedFile):
    xLightsFile = "inputSequences/" + inputFile
    orderedFile = "channelOrderSequences/" + orderedFile
    outFile = "outputSequences/" + inputFile
    error_channels = []
    # parse a well-formed LOR LMS file for reference
    LORroot, channelDict, dummyList = parseLMSfromLOR(orderedFile)
    # create a new sequence XML object based on the previous one
    oldRoot, effectDict = parseLMSfromXLights(xLightsFile)
    newSeq = ET.Element('sequence')
    newSeq.set("saveFileVersion", LORroot.get("saveFileVersion"))
    oldMusicFilename = oldRoot.get("musicFilename")
    newMusicFileName = ntpath.basename(oldMusicFilename)
    newSeq.set("musicFilename", newMusicFileName)
    # set channels and effects based on a combo of old xLights LMS file and well-formed LOR LMS file
    channels = ET.SubElement(newSeq, 'channels')
    for oldChannelNum in channelDict:
        if oldChannelNum not in effectDict:
            error_channels.append(oldChannelNum)
            continue
        oldChannel = channelDict[oldChannelNum]
        newChannel = newChannelFromOldChannel(oldChannel)
        newChannel.extend(effectDict[oldChannelNum])
        channels.append(newChannel)
    # add the missing channel
    if 322 in error_channels:
        fifteen_two = make_fifteen_two()
        channels.append(fifteen_two)
    # display errors
    print("error with channel(s)")
    print(error_channels)
    # add dummy channels
    channels.extend(dummyList)
    # add rgbChannels, cosmicColorDevices, and channelGroupLists
    LORchannel = LORroot.find("channels")
    rgbChannels = LORchannel.findall("rgbChannel")
    channels.extend(rgbChannels)
    cosmicColorDevices = LORchannel.findall("cosmicColorDevice")
    channels.extend(cosmicColorDevices)
    channelGroupLists = LORchannel.findall("channelGroupList")
    channels.extend(channelGroupLists)
    # add the timing grid from LOR
    timingGrids = LORroot.find("timingGrids")
    newSeq.append(timingGrids)
    newSeqTree = ET.ElementTree(newSeq)
    # set tracks based on the length of xLights file and saved indexes of LOR file
    tracks = LORroot.find("tracks")
    track = tracks.find("track")
    oldTrack = oldRoot.find("tracks/track")
    track.set("totalCentiseconds", oldTrack.get("totalCentiseconds"))
    newSeq.append(tracks)
    # add the animation designed in LOR
    animation = LORroot.find("animation")
    newSeq.append(animation)
    newSeqTree.write(outFile)
    return newSeq



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('input_file')
    parser.add_argument('correct_order_file')
    args = parser.parse_args()

    reconstructSequence(args.input_file, args.correct_order_file)

