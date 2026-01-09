# Needs Investigation

Promising issues that need more analysis before we can determine a solution.

---

## Issues

### #11233 - Multi-frame MSP responses over CRSF lose first frame

**Created:** 2024-12-28
**Labels:** bug
**URL:** https://github.com/iNavFlight/inav/issues/11233

**Problem:**
Detailed bug report about CRSF MSP framing issue. Multi-frame MSP responses over CRSF protocol are losing the first frame.

**Investigation Needed:**
- Review CRSF MSP handling code
- Understand multi-frame response assembly
- May be timing or buffer issue

**Notes:**
Good bug report with technical details.

---

### #11156 - ADSB Warning Message not showing in OSD

**Created:** 2025-12-02
**Labels:** bug
**URL:** https://github.com/iNavFlight/inav/issues/11156

**Problem:**
ADSB warning messages are not appearing in the OSD when they should.

**Investigation Needed:**
- Check OSD element configuration
- Verify ADSB warning trigger conditions
- May be simple OSD element issue

**Notes:**
Could be readily solvable once root cause is identified.

---

### #9633 - LED strip RED color shows as pink

**Created:** 2024-01-12
**Labels:** Bugfix
**URL:** https://github.com/iNavFlight/inav/issues/9633

**Problem:**
When LED strip is set to COLOR mode with RED (color #2), LED shows pink instead of red. However, GPS mode "no fix" indicator shows correct red color.

**Investigation Needed:**
- Compare color table values for COLOR mode vs GPS mode
- May be a simple color value fix

**Notes:**
Has video evidence. Could be simple color table fix once values are identified.

---

### #9195 - Altitude and speed scroll bars move wrong direction

**Created:** 2023-07-25
**Labels:** Bugfix, Enhancement
**URL:** https://github.com/iNavFlight/inav/issues/9195

**Problem:**
OSD altitude and speed scroll bars move in the inverse direction of how they should. When airspeed reduces and altitude increases, the bars move opposite to standard aviation instruments (like Garmin).

**Investigation Needed:**
- Review OSD scroll bar rendering logic
- Compare with reference video of correct behavior
- May just need to negate a value

**Notes:**
Has DVR clip showing issue and reference video showing correct behavior. Likely simple sign flip fix.
