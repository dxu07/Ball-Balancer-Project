'''!
    @file       motor.py
    
    @brief      Motor class to initialize and set up the motors in DRV8847.py
    
    @details    This motor class initializes the pins with the motor object to 
                be enabled. Additionally, it allows for a pulse width modulation
                control that changes the speed of the motor. This allows for the
                Motor to move clockwise and counterclockwise at difference 
                speeds.

'''
import pyb, time
from pyb import Pin, Timer

class Motor:
    '''!    
        @brief      A motor class for one channel of the DRV8847.
        @details    Objects of this class can be used to apply PWM to a given
                    DC motor.
    '''

    def __init__ (self, PWM_tim, IN1_pin, IN2_pin, motorNum):
        '''!
            @brief      Initializes and returns an object associated with a DC Motor.
            @details    Objects of this class should not be instantiated
                        directly. Instead create a DRV8847 object and use
                        that to create Motor objects using the method
                        DRV8847.motor().
        '''
        
        self.IN1 = pyb.Pin(IN1_pin, pyb.Pin.OUT_PP)
        self.IN2 = pyb.Pin(IN2_pin, pyb.Pin.OUT_PP)
        if motorNum == 1:
            self.chanA = 1
            self.chanB = 2
        elif motorNum == 2:
            self.chanA = 3
            self.chanB = 4    
        self.timch1 = PWM_tim.channel(self.chanA, pyb.Timer.PWM_INVERTED, pin=self.IN1)
        self.timch2 = PWM_tim.channel(self.chanB, pyb.Timer.PWM_INVERTED, pin=self.IN2)
        pass
    
    def set_duty (self, duty):
        '''!
            @brief      Set the PWM duty cycle for the motor channel.
            @details    This method sets the duty cycle to be sent
                        to the motor to the given level. Positive values
                        cause effort in one direction, negative values
                        in the opposite direction.
            @param duty A signed number holding the duty
                        cycle of the PWM signal sent to the motor
        '''
        if duty > 0:
            self.timch1.pulse_width_percent(0)
            self.timch2.pulse_width_percent(duty)
        elif duty < 0:
            self.timch1.pulse_width_percent(duty*-1)
            self.timch2.pulse_width_percent(0)
        else:
            self.timch1.pulse_width_percent(0)
            self.timch2.pulse_width_percent(0)
        pass
    
    
if __name__ == '__main__':

    # Adjust the following code to write a test program for your motor class. Any
    # code within the if __name__ == '__main__' block will only run when the
    # script is executed as a standalone program. If the script is imported as
    # a module the code block will not run.
    
    # Create a timer object to use for motor control
    PWM_tim = Timer(3, freq = 20_000)
    
    # Create a motor driver object and two motor objects. You will need to
    # modify the code to facilitate passing in the pins and timer objects needed
    # to run the motors.
    motor_1 = Motor(PWM_tim, Pin.cpu.B4, Pin.cpu.B5, 1)
    motor_2 = Motor(PWM_tim, Pin.cpu.B0, Pin.cpu.B1, 2)
    
    # Enable the motor driver
    nSLEEP = Pin(Pin.cpu.A15, mode=Pin.OUT_PP)
    nSLEEP.high()
    
    # Set the duty cycle of the first motor to 40 percent
    motor_1.set_duty(100)
    time.sleep(1)
    motor_1.set_duty(0)
    time.sleep(1)
    motor_2.set_duty(100)
    time.sleep(1)
    motor_2.set_duty(0)
    time.sleep(1)
    motor_1.set_duty(-100)
    time.sleep(1)
    motor_1.set_duty(0)
    time.sleep(1)
    motor_2.set_duty(-100)
    time.sleep(1)
    nSLEEP.low()