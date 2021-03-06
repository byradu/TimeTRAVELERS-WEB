from .model import TimeSegment
from .util import NlpUtil
from .util import RegexUtil
from .util import TokenTypeUtil
import xml.etree.ElementTree as ET
from datetime import datetime as dt

class SynTime(object):
    """
    SynTime APIs.
    """

    def __init__(self):
        self.arrayOfValues = []
        self.__nlpUtil = NlpUtil()
        self.__regexUtil = RegexUtil()
        self.__tokenTypeUtil = TokenTypeUtil(self.__regexUtil)

    def extractTimexFromText(self, text, date):
        """
        Extract timex (time expressions) from text.

        Args:
            text (str): Raw text to extract timex from.
            date (str)
        """
        if not text:
            return text
        taggedTokenList = self.__nlpUtil.tagging(text)
        timeTokenList = self.__identifyTimeToken(taggedTokenList)
        if not timeTokenList:
            return text
        timeSegmentList = self.__identifyTimeSegment(taggedTokenList, timeTokenList)
        if not timeSegmentList:
            return text
        return self.__generateTimeMLText(text, taggedTokenList, timeSegmentList, date)

    def __identifyTimeToken(self, taggedTokenList):
        """
        Get time token list from taggedTokenList.

        Args:
            taggedTokenList (list): Tagged token list.

        Returns:
            timeTokenList (list): Time token index list.
        """
        timeTokenList = []
        for i in range(len(taggedTokenList)):
            taggedToken = taggedTokenList[i]
            token = taggedToken.token
            tag = taggedToken.tag

            tokenTypeSet = self.__tokenTypeUtil.getTokenTypeSet(token, tag)
            taggedToken.tokenTypeSet = tokenTypeSet
            #
            # if TokenTypeUtil.isHalfDayToken(taggedToken):
            #     if token.lower() == 'am' or token.lower() == 'pm':
            #         if i == 0 or (not TokenTypeUtil.isNumeralToken(taggedTokenList[i - 1])
            #                       and not TokenTypeUtil.isTimeToken(taggedTokenList[i - 1])):
            #             taggedToken.clearTokenType()
            # elif TokenTypeUtil.isTimeZoneToken(taggedToken):
            #     if i == 0 or not TokenTypeUtil.isTimeToken(taggedTokenList[i - 1]) \
            #             and not TokenTypeUtil.isHalfDayToken(taggedTokenList[i - 1]) \
            #             and not TokenTypeUtil.isNumeralToken(taggedTokenList[i - 1]):
            #         taggedToken.clearTokenType()
            if TokenTypeUtil.isEraToken(taggedToken):
                if i == 0 or not TokenTypeUtil.isNumeralToken(taggedTokenList[i - 1]):
                    taggedToken.clearTokenType()
            elif TokenTypeUtil.isYearToken(taggedToken):
                if i > 0 or taggedTokenList[i - 1].token.lower() == 'the':
                        # and (TokenTypeUtil.isInArticleToken(taggedTokenList[i - 1]) or taggedTokenList[i - 1].token.lower() == 'the'):
                    taggedTokenList[i - 1].clearTokenType()

            if TokenTypeUtil.isGeneralTimeToken(taggedToken):
                timeTokenList.append(i)

        return timeTokenList

    def __identifyTimeSegment(self, taggedTokenList, timeTokenList):
        """
        Get time segment list from taggedTokenList and timeTokenList.

        Args:
            taggedTokenList (list): Tagged token list.
            timeTokenList (list): Time token position list.

        Returns:
            timeSegmentList (list): Time segment list.
        """
        timeSegmentList = []
        firstToken = 0
        lastToken = len(taggedTokenList) - 1
        timeTokenLen = len(timeTokenList)
        for i in range(timeTokenLen):
            timeTokenPosition = timeTokenList[i]

            beginToken = timeTokenPosition
            endToken = timeTokenPosition

            taggedTimeToken = taggedTokenList[timeTokenPosition]
            if TokenTypeUtil.isPeriodToken(taggedTimeToken) or TokenTypeUtil.isDurationToken(taggedTimeToken):
                timeSegmentList.append(TimeSegment(timeTokenPosition, beginToken, endToken))
                continue

            leftBound = firstToken
            rightBound = lastToken
            if i > 0:
                leftBound = timeTokenList[i - 1] + 1
            if i < timeTokenLen - 1:
                rightBound = timeTokenList[i + 1] - 1

            # Search its left side
            findLeftDependentSegment = False
            leftTimeTokenPosition = -1
            leftBeginToken = leftTimeTokenPosition
            leftEndToken = leftTimeTokenPosition
            j = timeTokenPosition - 1
            while j >= leftBound:
                taggedPreMod = taggedTokenList[j]
                if TokenTypeUtil.isPrefixToken(taggedPreMod) or TokenTypeUtil.isNumeralToken(taggedPreMod):
                        # or TokenTypeUtil.isInArticleToken(taggedPreMod):
                    beginToken = j
                # elif TokenTypeUtil.isCommaToken(taggedPreMod):
                #     beginToken = j
                #     break
                elif TokenTypeUtil.isLinkageToken(taggedPreMod):
                    if j - 1 >= leftBound and TokenTypeUtil.isGeneralTimeToken(taggedTimeToken) \
                            and TokenTypeUtil.isNumeralToken(taggedTokenList[j - 1]):
                        findLeftDependentSegment = True
                        leftTimeTokenPosition = j - 1
                        leftBeginToken = leftTimeTokenPosition
                        leftEndToken = leftTimeTokenPosition
                        k = leftTimeTokenPosition - 1
                        while k >= leftBound:
                            if TokenTypeUtil.isPrefixToken(taggedPreMod) or TokenTypeUtil.isNumeralToken(taggedPreMod):
                                    # or TokenTypeUtil.isInArticleToken(taggedPreMod):
                                leftBeginToken = k
                                k -= 1
                            else:
                                break
                        beginToken = j + 1
                    else:
                        beginToken = j
                    break
                else:
                    break
                j -= 1

            # Search its right side
            findRightDependentSegment = False
            rightTimeTokenPosition = 0
            rightBeginToken = rightTimeTokenPosition
            rightEndToken = rightTimeTokenPosition
            j = timeTokenPosition + 1
            while j <= rightBound:
                taggedSufMod = taggedTokenList[j]
                if TokenTypeUtil.isSuffixToken(taggedSufMod) or TokenTypeUtil.isNumeralToken(taggedSufMod):
                    endToken = j
                # elif TokenTypeUtil.isCommaToken(taggedSufMod):
                #     endToken = j
                #     break
                elif TokenTypeUtil.isLinkageToken(taggedSufMod):
                    if j + 1 <= rightBound and TokenTypeUtil.isGeneralTimeToken(taggedTimeToken) \
                            and TokenTypeUtil.isNumeralToken(taggedTokenList[j + 1]):
                        findRightDependentSegment = True
                        rightTimeTokenPosition = j + 1
                        rightBeginToken = rightTimeTokenPosition
                        rightEndToken = rightTimeTokenPosition
                        k = rightTimeTokenPosition + 1
                        while k <= rightBound:
                            if TokenTypeUtil.isSuffixToken(taggedSufMod) or TokenTypeUtil.isNumeralToken(taggedSufMod):
                                rightEndToken = k
                                k += 1
                            else:
                                break
                        endToken = j - 1
                    else:
                        endToken = j
                    break
                else:
                    break
                j += 1

            if findLeftDependentSegment:
                timeSegmentList.append(TimeSegment(leftTimeTokenPosition, leftBeginToken, leftEndToken))
            timeSegmentList.append(TimeSegment(timeTokenPosition, beginToken, endToken))
            if findRightDependentSegment:
                timeSegmentList.append(TimeSegment(rightTimeTokenPosition, rightBeginToken, rightEndToken))

        return timeSegmentList

    def __generateTimeMLText(self, text, taggedTokenList, timeSegmentList, date):
        """
        Generate TimeML text for input.txt text.

        Args:
            text (str): Raw text.
            taggedTokenList (list): Tagged token list.
            timeSegmentList (list): Time segment list.
            date (str): User-specified date.

        Returns:
            timeMLText (str): Text in TimeML format.
        """
        timeMLText = ''
        type = None
        value = date
        tid = 1
        regexUtil = RegexUtil()
        tokenTypeUtil = TokenTypeUtil(regexUtil)
        lastCharPosition = 0
        taggedTokenListLen = len(taggedTokenList)
        timeSegmentListLen = len(timeSegmentList)

        xml_doc = ET.Element('TimeML')
        # DOCNO tag
        DOCNO = ET.SubElement(xml_doc, 'DOCNO').text = str(dt.today())
        # DOCTYPE tag
        DOCTYPE = ET.SubElement(xml_doc, 'DOCTYPE', SOURCE="filename")
        # BODY tag
        BODY = ET.SubElement(xml_doc, 'BODY')
        # TEXT tag
        TEXT = ET.SubElement(BODY, 'TEXT')

        if timeSegmentList and timeSegmentListLen > 0:
            isTimex = True
            timexBeginTokenPosition = timeSegmentList[0].beginTokenPosition
            timexEndTokenPosition = timeSegmentList[0].endTokenPosition

            for i in range(timeSegmentListLen):
                timeSegment = timeSegmentList[i]
                segmentBeginTokenPosition = timeSegment.beginTokenPosition
                segmentEndTokenPosition = timeSegment.endTokenPosition
                if timexEndTokenPosition + 1 == segmentBeginTokenPosition or timexEndTokenPosition > segmentBeginTokenPosition:
                    isTimex = False
                elif timexEndTokenPosition == segmentBeginTokenPosition:
                    if TokenTypeUtil.isLinkageToken(taggedTokenList[segmentBeginTokenPosition]):
                        isTimex = True
                    else:
                        isTimex = False
                else:
                    isTimex = True

                if not isTimex:
                    timexEndTokenPosition = segmentEndTokenPosition
                else:
                    timexBeginTaggedToken = taggedTokenList[timexBeginTokenPosition]
                    timexEndTaggedToken = taggedTokenList[timexEndTokenPosition]
                    if TokenTypeUtil.isLinkageToken(timexBeginTaggedToken) or timexBeginTaggedToken.tag == 'IN':
                        # TokenTypeUtil.isCommaToken(timexBeginTaggedToken) or
                        timexBeginTokenPosition += 1
                    if TokenTypeUtil.isLinkageToken(timexEndTaggedToken):
                        # TokenTypeUtil.isComma(timexEndTaggedToken) or
                        timexEndTokenPosition -= 1

                    timexEndToken = timexEndTaggedToken.token
                    beginCharPosition = timexBeginTaggedToken.beginCharPosition
                    endCharPosition = timexEndTaggedToken.endCharPosition

                    # timeMLText += text[lastCharPosition:beginCharPosition]
                    lastCharPosition = beginCharPosition

                    index = timexBeginTokenPosition
                    while index <= timexEndTokenPosition:
                        temTaggedToken = taggedTokenList[index]
                        if TokenTypeUtil.isDurationToken(temTaggedToken) or TokenTypeUtil.isDurationDurationToken(temTaggedToken) \
                             or TokenTypeUtil.isDecadeToken(temTaggedToken) or TokenTypeUtil.isTimeUnitToken(temTaggedToken) \
                             or (TokenTypeUtil.isPrefixToken(temTaggedToken) and TokenTypeUtil.isDurationToken(temTaggedToken)):
                            type = 'DURATION'
                        elif tokenTypeUtil.isYearToken(temTaggedToken) or tokenTypeUtil.isYearYearToken(temTaggedToken) \
                                or tokenTypeUtil.isWeekToken(temTaggedToken) or tokenTypeUtil.isSeasonToken(
                            temTaggedToken) \
                                or tokenTypeUtil.isHolidayToken(temTaggedToken) or tokenTypeUtil.isDateToken(
                            temTaggedToken) \
                                or tokenTypeUtil.isMonthToken(temTaggedToken) or tokenTypeUtil.isMonthMonthToken(
                            temTaggedToken) \
                                or tokenTypeUtil.isTimeLineToken(temTaggedToken) or tokenTypeUtil.isYearMonthToken(
                            temTaggedToken) \
                                or tokenTypeUtil.isWeekToken(temTaggedToken) or tokenTypeUtil.isWeekWeekToken(
                            temTaggedToken) \
                                or tokenTypeUtil.isDateToken(temTaggedToken):
                            type = 'DATE'
                        elif TokenTypeUtil.isTimeToken(temTaggedToken) or TokenTypeUtil.isTimeTimeToken(temTaggedToken) \
                                or TokenTypeUtil.isHalfDayToken(temTaggedToken) or TokenTypeUtil.isHalfDayHalfDayToken(
                            temTaggedToken) \
                               or TokenTypeUtil.isEraToken(
                            temTaggedToken) \
                                or TokenTypeUtil.isDayTimeToken(temTaggedToken) or TokenTypeUtil.isTimeLineToken(
                            temTaggedToken) \
                                or TokenTypeUtil.isGeneralTimeToken(temTaggedToken):
                            type = 'TIME'
                        elif TokenTypeUtil.isPeriodToken(temTaggedToken):
                            type = 'SET'
                        else:
                            type = "Not found"
                        index += 1

                    if timexEndToken.endswith('\'s'):
                        timex = text[lastCharPosition:endCharPosition - 2]
                        timeMLText += SynTime.__getTIMEX3Str(tid, type, value, timex)
                        self.arrayOfValues.append(timex)
                        tag = ET.SubElement(TEXT, 'TIMEEX', id=str(tid), value=str(timex), type=type).text = str(timex)
                        lastCharPosition = endCharPosition - 2
                    elif timexEndToken.endswith('s') \
                            and (timexEndTokenPosition + 1 < taggedTokenListLen and
                                 taggedTokenList[timexEndTokenPosition + 1].token == "'"):
                        timex = text[lastCharPosition:taggedTokenList[timexEndTokenPosition + 1].endCharPosition]
                        timeMLText += SynTime.__getTIMEX3Str(tid, type, value, timex)
                        self.arrayOfValues.append(timex)
                        tag = ET.SubElement(TEXT, 'TIMEEX', id=str(tid), value=str(timex), type=type).text = str(timex)
                        lastCharPosition = taggedTokenList[timexEndTokenPosition + 1].endCharPosition
                    else:
                        timex = text[lastCharPosition:endCharPosition]
                        timeMLText += SynTime.__getTIMEX3Str(tid, type, value, timex)
                        self.arrayOfValues.append(timex)
                        tag = ET.SubElement(TEXT, 'TIMEEX', id=str(tid), value=str(timex), type=type).text = str(timex)
                        lastCharPosition = endCharPosition
                    tid += 1
                    timexBeginTokenPosition = segmentBeginTokenPosition
                    timexEndTokenPosition = segmentEndTokenPosition

            timexBeginTaggedToken = taggedTokenList[timexBeginTokenPosition]
            timexEndTaggedToken = taggedTokenList[timexEndTokenPosition]
            if TokenTypeUtil.isLinkageToken(timexBeginTaggedToken) or timexBeginTaggedToken.tag == 'IN':
                # TokenTypeUtil.isCommaToken(timexBeginTaggedToken) or
                timexBeginTokenPosition += 1
            if TokenTypeUtil.isLinkageToken(timexEndTaggedToken):
                # TokenTypeUtil.isComma(timexEndTaggedToken) or
                timexEndTokenPosition -= 1

            timexEndToken = timexEndTaggedToken.token
            beginCharPosition = timexBeginTaggedToken.beginCharPosition
            endCharPosition = timexEndTaggedToken.endCharPosition

            # timeMLText += text[lastCharPosition:beginCharPosition]
            lastCharPosition = beginCharPosition

            index = timexBeginTokenPosition
            while index <= timexEndTokenPosition:
                temTaggedToken = taggedTokenList[index]
                if TokenTypeUtil.isDurationToken(temTaggedToken) or TokenTypeUtil.isDurationDurationToken(temTaggedToken)\
                     or TokenTypeUtil.isDecadeToken(temTaggedToken) or TokenTypeUtil.isTimeUnitToken(temTaggedToken)\
                     or (TokenTypeUtil.isPrefixToken(temTaggedToken) and TokenTypeUtil.isDurationToken(temTaggedToken)):
                    type = 'DURATION'
                elif tokenTypeUtil.isYearToken(temTaggedToken) or tokenTypeUtil.isYearYearToken(temTaggedToken) \
                    or tokenTypeUtil.isWeekToken(temTaggedToken) or tokenTypeUtil.isSeasonToken(temTaggedToken) \
                    or tokenTypeUtil.isHolidayToken(temTaggedToken) or tokenTypeUtil.isDateToken(temTaggedToken)\
                    or tokenTypeUtil.isMonthToken(temTaggedToken) or tokenTypeUtil.isMonthMonthToken(temTaggedToken)\
                    or tokenTypeUtil.isTimeLineToken(temTaggedToken) or tokenTypeUtil.isYearMonthToken(temTaggedToken) \
                    or tokenTypeUtil.isWeekToken(temTaggedToken) or tokenTypeUtil.isWeekWeekToken(temTaggedToken) \
                    or tokenTypeUtil.isDateToken(temTaggedToken):
                    type = 'DATE'
                elif TokenTypeUtil.isTimeToken(temTaggedToken) or TokenTypeUtil.isTimeTimeToken(temTaggedToken)\
                     or TokenTypeUtil.isHalfDayToken(temTaggedToken) or TokenTypeUtil.isHalfDayHalfDayToken(temTaggedToken)  \
                     or TokenTypeUtil.isEraToken(temTaggedToken)\
                     or TokenTypeUtil.isDayTimeToken(temTaggedToken) or TokenTypeUtil.isTimeLineToken(temTaggedToken)\
                     or TokenTypeUtil.isGeneralTimeToken(temTaggedToken):
                    type = 'TIME'
                elif TokenTypeUtil.isPeriodToken(temTaggedToken):
                    type = 'SET'
                else:
                    type="Not found"
                index += 1

            if timexEndToken.endswith('\'s'):
                timex = text[lastCharPosition:endCharPosition - 2]
                timeMLText += SynTime.__getTIMEX3Str(tid, type, value, timex)
                self.arrayOfValues.append(timex)
                tag = ET.SubElement(TEXT, 'TIMEEX', id=str(tid), value=str(timex), type=type).text = str(timex)
                lastCharPosition = endCharPosition - 2
            elif timexEndToken.endswith('s') and (timexEndTokenPosition + 1 < taggedTokenListLen and
                    taggedTokenList[timexEndTokenPosition + 1].token == "'"):
                timex = text[lastCharPosition:taggedTokenList[timexEndTokenPosition + 1].endCharPosition]
                timeMLText += SynTime.__getTIMEX3Str(tid, type, value, timex)
                self.arrayOfValues.append(timex)
                tag = ET.SubElement(TEXT, 'TIMEEX', id=str(tid), value=str(timex), type=type).text = str(timex)

                lastCharPosition = taggedTokenList[timexEndTokenPosition + 1].endCharPosition
            else:
                timex = text[lastCharPosition:endCharPosition]
                timeMLText += SynTime.__getTIMEX3Str(tid, type, value, timex)
                self.arrayOfValues.append(timex)
                tag = ET.SubElement(TEXT, 'TIMEEX', id=str(tid), value=str(timex), type=type).text = str(timex)
                lastCharPosition = endCharPosition
            tid += 1

        # timeMLText += text[lastCharPosition:]
        tree = ET.ElementTree(xml_doc)
        tree.write(r'templates\pysyntime\resource\outputXML.xml', encoding='UTF-8', xml_declaration=True)
        return timeMLText, self.arrayOfValues

    @classmethod
    def __getTIMEX3Str(cls, tid, timexType, value, timex):
        TIMEX3_TID = "<TIMEX3 tid=\"t"
        TIMEX3_TYPE = "\" type=\""
        TIMEX3_VALUE = "\" value=\""
        TIMEX3_MID = "\">"
        TIMEX3_END = "</TIMEX3>"
        return TIMEX3_TID + str(tid) + TIMEX3_TYPE + timexType + TIMEX3_VALUE + timex + TIMEX3_MID + '\n' + '   '+timex + '\n' + TIMEX3_END + '\n'

