# -*- coding: utf-8 -*-
import unittest
import plivohelper
import re

class PlivoTest(unittest.TestCase):
    def strip(self, xml):
        return re.sub(r'\n|\t', '', str(xml).strip())

    def improperAppend(self, verb):
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Speak(""))
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.GetDigits())
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Play(""))
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Record())
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Hangup())
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Redirect())
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Dial())
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Conference(""))
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Wait())

class TestResponse(PlivoTest):

    def testEmptyResponse(self):
        r = plivohelper.Response()
        self.assertEquals(self.strip(r), "<Response/>")

class TestSpeak(PlivoTest):

    def testEmptySpeak(self):
        """should be a say with no text"""
        r = plivohelper.Response()
        r.append(plivohelper.Speak(""))
        self.assertEquals(self.strip(r), '<Response><Speak/></Response>')

    def testSpeakHelloWorld(self):
        """should say hello monkey"""
        r = plivohelper.Response()
        r.append(plivohelper.Speak("Hello World"))
        r = self.strip(r)
        self.assertEquals(r, '<Response><Speak>Hello World</Speak></Response>')

    def testSpeakLoop(self):
        """should say hello monkey and loop 3 times"""
        r = plivohelper.Response()
        r.append(plivohelper.Speak("Hello Monkey", loop=3))
        r = self.strip(r)
        self.assertEquals(r, '<Response><Speak loop="3">Hello Monkey</Speak></Response>')

    def testSpeakAddAttribute(self):
        """add attribute"""
        self.assertRaises(plivohelper.PlivoException,
                          plivohelper.Speak, "", foo="bar")

    def testSpeakBadAppend(self):
        """ should raise exceptions for wrong appending"""
        self.improperAppend(plivohelper.Speak(""))

class TestPlay(PlivoTest):

    def testEmptyPlay(self):
        """should play hello monkey"""
        r = plivohelper.Response()
        r.append(plivohelper.Play(""))
        r = self.strip(r)
        self.assertEqual(r,"<Response><Play/></Response>")

    def testPlayHello(self):
        """should play hello monkey"""
        r = plivohelper.Response()
        r.append(plivohelper.Play("http://hellomonkey.mp3"))
        r = self.strip(r)
        self.assertEqual(r, '<Response><Play>http://hellomonkey.mp3</Play></Response>')

    def testPlayHelloLoop(self):
        """should play hello monkey loop"""
        r = plivohelper.Response()
        r.append(plivohelper.Play("http://hellomonkey.mp3", loop=3))
        r = self.strip(r)
        self.assertEqual(r, '<Response><Play loop="3">http://hellomonkey.mp3</Play></Response>')

    def testPlayConvienceMethod(self):
        """convenience method: should play hello monkey"""
        r = plivohelper.Response()
        r.addPlay("http://hellomonkey.mp3", loop=3)
        r = self.strip(r)
        self.assertEqual(r, '<Response><Play loop="3">http://hellomonkey.mp3</Play></Response>')

    def testPlayAddAttribute(self):
        """add attribute"""
        self.assertRaises(plivohelper.PlivoException,
                          plivohelper.Play, "", foo="bar")

    def testPlayBadAppend(self):
        """ should raise exceptions for wrong appending"""
        self.improperAppend(plivohelper.Play(""))

class TestRecord(PlivoTest):

    def testRecordEmpty(self):
        """should record"""
        r = plivohelper.Response()
        r.append(plivohelper.Record())
        r = self.strip(r)
        self.assertEquals(r, '<Response><Record/></Response>')

    def testRecordMaxlengthFinishTimeout(self):
        """should record with an maxlength, finishonkey, and timeout"""
        r = plivohelper.Response()
        r.append(plivohelper.Record(timeout=4,finishOnKey="#", maxLength=30))
        r = self.strip(r)
        self.assertEquals(r, '<Response><Record finishOnKey="#" maxLength="30" timeout="4"/></Response>')
  
    def testRecordMaxlengthFinishTimeout(self):
        """should record with an maxlength, finishonkey, and timeout"""
        r = plivohelper.Response()
        r.addRecord(timeout=4,finishOnKey="#", maxLength=30)
        r = self.strip(r)
        self.assertEquals(r, '<Response><Record finishOnKey="#" maxLength="30" timeout="4"/></Response>')

    def testRecordAddAttribute(self):
        """add attribute"""
        self.assertRaises(plivohelper.PlivoException,
                          plivohelper.Record, foo="bar")

    def testRecordBadAppend(self):
        """ should raise exceptions for wrong appending"""
        self.improperAppend(plivohelper.Record())

class TestRedirect(PlivoTest):

    def testRedirectEmpty(self):
        r = plivohelper.Response()
        r.append(plivohelper.Redirect())
        r = self.strip(r)
        self.assertEquals(r, '<Response><Redirect/></Response>')

    def testRedirectMethod(self):
        r = plivohelper.Response()
        r.append(plivohelper.Redirect(url="example.com", method="POST"))
        r = self.strip(r)
        self.assertEquals(r, '<Response><Redirect method="POST">example.com</Redirect></Response>')

    def testRedirectMethodGetParams(self):
        r = plivohelper.Response()
        r.append(plivohelper.Redirect(url="example.com?id=34&action=hey", method="POST"))
        r = self.strip(r)
        self.assertEquals(r, '<Response><Redirect method="POST">example.com?id=34&amp;action=hey</Redirect></Response>')

    def testAddAttribute(self):
        """add attribute"""
        self.assertRaises(plivohelper.PlivoException,
                          plivohelper.Redirect, "", foo="bar")

    def testBadAppend(self):
        """ should raise exceptions for wrong appending"""
        self.improperAppend(plivohelper.Redirect())


class TestHangup(PlivoTest):

    def testHangup(self):
        """convenience: should Hangup to a url via POST"""
        r = plivohelper.Response()
        r.append(plivohelper.Hangup())
        r = self.strip(r)
        self.assertEquals(r, '<Response><Hangup/></Response>')

    def testHangupConvience(self):
        """convenience: should Hangup to a url via POST"""
        r = plivohelper.Response()
        r.addHangup()
        r = self.strip(r)
        self.assertEquals(r, '<Response><Hangup/></Response>')

    def testSchedule(self):
        r = plivohelper.Response()
        r.addHangup(schedule=10)
        r = self.strip(r)
        self.assertEquals(r, '<Response><Hangup schedule="10"/></Response>')

    def testSchedule(self):
        r = plivohelper.Response()
        r.addHangup(reason="rejected")
        r = self.strip(r)
        self.assertEquals(r, '<Response><Hangup reason="rejected"/></Response>')

    def testAddAttribute(self):
        self.assertRaises(plivohelper.PlivoException,
                          plivohelper.Hangup, foo="bar")

    def testBadAppend(self):
        """ should raise exceptions for wrong appending"""
        self.improperAppend(plivohelper.Hangup())


class TestDial(PlivoTest):

    def testDial(self):
        """ should redirect the call"""
        r = plivohelper.Response()
        r.append(plivohelper.Dial("1231231234"))
        r = self.strip(r)
        self.assertEquals(r, '<Response><Dial><Number>1231231234</Number></Dial></Response>')

    def testConvienceMethod(self):
        """ should dial to a url via post"""
        r = plivohelper.Response()
        r.addDial()
        r = self.strip(r)
        self.assertEquals(r, '<Response><Dial/></Response>')

    def testAddNumber(self):
        """add a number to a dial"""
        r = plivohelper.Response()
        d = plivohelper.Dial()
        d.append(plivohelper.Number("1231231234"))
        r.append(d)
        r = self.strip(r)
        self.assertEquals(r, '<Response><Dial><Number>1231231234</Number></Dial></Response>')

    def testAddNumberConvience(self):
        """add a number to a dial, convience method"""
        r = plivohelper.Response()
        d = r.addDial()
        d.addNumber("1231231234")
        r = self.strip(r)
        self.assertEquals(r, '<Response><Dial><Number>1231231234</Number></Dial></Response>')

class TestConference(PlivoTest):

    def testAddConference(self):
        """ add a conference to a dial"""
        r = plivohelper.Response()
        r.append(plivohelper.Conference("My Room"))
        r = self.strip(r)
        self.assertEquals(r, '<Response><Conference>My Room</Conference></Response>')

    def testAddConferenceConvenceMethod(self):
        """ add a conference to a dial, conviently"""
        r = plivohelper.Response()
        r.addConference("My Room")
        r = self.strip(r)
        self.assertEquals(r, '<Response><Conference>My Room</Conference></Response>')

    def testAddAttribute(self):
        """add attribute"""
        self.assertRaises(plivohelper.PlivoException,
                    plivohelper.Conference, "MyRoom", foo="bar")

    def testBadAppend(self):
        """ should raise exceptions for wrong appending"""
        self.improperAppend(plivohelper.Conference("Hello"))


class TestGetDigits(PlivoTest):

    def testEmpty(self):
        """ a gather with nothing inside"""
        r = plivohelper.Response()
        r.append(plivohelper.GetDigits())
        r = self.strip(r)
        self.assertEquals(r, '<Response><GetDigits/></Response>')

    def testAddAttribute(self):
        """add attribute"""
        self.assertRaises(plivohelper.PlivoException,
                    plivohelper.GetDigits, foo="bar")

    def testNestedSpeakPlayWait(self):
        """ a gather with a say, play, and pause"""
        r = plivohelper.Response()
        g = plivohelper.GetDigits()
        g.append(plivohelper.Speak("Hey"))
        g.append(plivohelper.Play("hey.mp3"))
        g.append(plivohelper.Wait())
        r.append(g)
        r = self.strip(r)
        self.assertEquals(r, '<Response><GetDigits><Speak>Hey</Speak><Play>hey.mp3</Play><Wait/></GetDigits></Response>')


    def testNestedSpeakPlayWaitConvience(self):
        """ a gather with a say, play, and pause"""
        r = plivohelper.Response()
        g = r.addGetDigits()
        g.addSpeak("Hey")
        g.addPlay("hey.mp3")
        g.addWait()
        r = self.strip(r)
        self.assertEquals(r, '<Response><GetDigits><Speak>Hey</Speak><Play>hey.mp3</Play><Wait/></GetDigits></Response>')

    def testImproperNesting(self):
        """ bad nesting"""
        verb = plivohelper.GetDigits()
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.GetDigits())
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Record())
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Hangup())
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Redirect())
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Dial())
        self.assertRaises(plivohelper.PlivoException, verb.append, plivohelper.Conference(""))

if __name__ == '__main__':
    unittest.main()
