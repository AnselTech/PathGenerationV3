class PID:

    def __init__(self, kp: float, ki: float, kd: float, min: float = 0, max: float = 100000, tolerance: float = None, toleranceRepeated: int = 1, disableOvershoot: bool = False):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min = min # min magnitude of output
        self.max = max # max magnitude of output
        self.tolerance = tolerance # +/- tolerance interval to be considered done
        self.toleranceRepeated = toleranceRepeated
        self.disableOvershoot = disableOvershoot # If true, will exit as soon as threshold is crossed

        self.prevError = 0
        self.prevIntegral = 0

        self.startedPositive = None
        self.repeatedTimes = 0

    # Run the PID for one tick. Return the output value
    def tick(self, error: float) -> float:

        self.error = error

        if self.startedPositive is None:
            self.startedPositive = error > 0

        integral = self.prevIntegral + error * 0.02
        derivative = (error - self.prevError) / 0.02

        output = self.kp * error + self.ki * integral + self.kd * derivative
        self.prevError = error
        self.prevIntegral = integral

        # Set mininum output value
        if output > 0:
            output = max(self.min, output)
        else:
            output = min(-self.min, output)
        
        output = max(-self.max, min(self.max, output))

        return output

    def isDone(self) -> bool:

        if self.disableOvershoot:
            return (self.error < 0) if self.startedPositive else (self.error > 0)

        elif self.tolerance is None:
            # if tolerance == none, object was not configured to have an exit condition
            raise Exception("No end condition tolerance specified")
        else:
            if abs(self.error) < self.tolerance:
                self.repeatedTimes += 1
            else:
                self.repeatedTimes = 0
            return self.repeatedTimes >= self.toleranceRepeated