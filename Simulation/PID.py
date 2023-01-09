class PID:

    def __init__(self, kp: float, ki: float, kd: float, min: float = 0, max: float = 100000, tolerance: float = None, toleranceRepeated: int = 1):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min = min # min magnitude of output
        self.max = max # max magnitude of output
        self.tolerance = tolerance # +/- tolerance interval to be considered done
        self.toleranceRepeated = toleranceRepeated

        self.prevError = 0
        self.prevIntegral = 0

    # Run the PID for one tick. Return the output value
    def tick(self, error: float) -> float:

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

        # if tolerance == none, object was not configured to have an exit condition
        if self.tolerance is None:
            raise Exception("No end condition tolerance specified")

