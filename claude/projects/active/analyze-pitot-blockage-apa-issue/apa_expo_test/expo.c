#include <stdio.h>
#include <math.h>

// Helper function to constrain a value between min and max
static inline float constrainf(float value, float min, float max) {
    if (value < min) return min;
    if (value > max) return max;
    return value;
}

static float calculateFixedWingAirspeedTPAFactorOrg(float airspeed){
    const float referenceAirspeed = 2000; // in cm/s
    float tpaFactor= powf(referenceAirspeed/(airspeed+0.01f), 1.3);
    tpaFactor= constrainf(tpaFactor, 0.3f, 2.0f);
    return tpaFactor;
}


static float calculateFixedWingAirspeedTPAFactorSmooth(float airspeed){
    // const float referenceAirspeed = 2000; // in cm/s
    float tpaFactor = 1 / powf(airspeed, 1.3) * 19608;
    tpaFactor= constrainf(tpaFactor, 0.3f, 2.0f);
    return tpaFactor;
}

int main() {
    for (float speed = 500; speed < 4000; speed += 25) {
        printf("%f,%f,%f\n", speed, calculateFixedWingAirspeedTPAFactorOrg(speed), calculateFixedWingAirspeedTPAFactorSmooth(speed));
    }
    return 0;
}


/*
static float calculateFixedWingAirspeedTPAFactor(void){
    const float airspeed = getAirspeedEstimate(); // in cm/s
    const float referenceAirspeed = pidProfile()->fixedWingReferenceAirspeed; // in cm/s
    float tpaFactor= powf(referenceAirspeed/(airspeed+0.01f), currentControlProfile->throttle.apa_pow/100.0f);
    tpaFactor= constrainf(tpaFactor, 0.3f, 2.0f);
    return tpaFactor;
}
*/



