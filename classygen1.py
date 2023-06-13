import rp2
from machine import Pin, Timer

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def pio_outdiv2():
	wrap_target()
	set(pins, 1)
	set(pins, 0)
	wrap()
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def pio_outdiv4():
	wrap_target()
	set(pins, 1) [1]
	set(pins, 0) [1]
	wrap()
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def pio_outdiv8():
	wrap_target()
	set(pins, 1) [3]
	set(pins, 0) [3]
	wrap()
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def pio_outdiv16():
	wrap_target()
	set(pins, 1) [7]
	set(pins, 0) [7]
	wrap()
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def pio_outdiv32():
	wrap_target()
	set(pins, 1) [15]
	set(pins, 0) [15]
	wrap()

# internal LED is GPIO 25, 
# very bottom right is DIP 21 / GPIO 16
# DIP in 22 (near bottom right) is GPIO 17
sm = rp2.StateMachine(0, pio_outdiv8, set_base=Pin(16))

def outputClock(freq_khz):
	#sm.active(0)
	# let's limit CPU to ~200MHz
	if freq_khz > 50000:
		rp2.StateMachine(0, pio_outdiv2, set_base=Pin(16))
		machine.freq(freq_khz*2000) # need to clock at twice the speed
	elif freq_khz > 28000:
		rp2.StateMachine(0, pio_outdiv4, set_base=Pin(16))
		machine.freq(freq_khz*4000) # need to clock at 4x the speed
	elif freq_khz > 10000:
		rp2.StateMachine(0, pio_outdiv8, set_base=Pin(16))
		machine.freq(freq_khz*8000) # need to clock at 4x the speed
	elif freq_khz > 1000:
		rp2.StateMachine(0, pio_outdiv16, set_base=Pin(16))
		machine.freq(freq_khz*16000) # need to clock at 4x the speed
	else:
		rp2.StateMachine(0, pio_outdiv32, set_base=Pin(16))
		machine.freq(freq_khz*32000) # need to clock at 4x the speed
	sm.active(1)

def blink(state):
	Pin(17, mode=Pin.OPEN_DRAIN, pull=Pin.PULL_UP, value=state)
	Pin(25, mode=Pin.OUT, value=state)


class SweepGen:
	def __init__(self, freqs=() ):
		self.freqList = list(freqs)
		self.i = 0
		self.timer = None
	
	def nextfreq(self):
		self.i += 1
		if self.i >= len(self.freqList):
			self.i = 0
			blink(1)
		else:
			blink(0)
		if len(self.freqList):
			freq = self.freqList[self.i]
			#print(freq)
			try:
				outputClock(freq)
			except ValueError:
				print("unachievable freq %d" % (freq) )
				self.freqList.remove(freq)
		
	def mycallback(self, timer):
		self.nextfreq()
	
	def stop(self):
		if self.timer:
			self.timer.deinit()
			self.timer = None
		
	def start(self, interval=1, timer_id=0):
		self.stop()
		if interval > 0:
			self.timer = Timer(mode=Timer.PERIODIC, period=interval, callback=self.mycallback)

def freqRange(center, width, step = 250):
	l = [center]
	for i in range(1, 100):
		low = center - i*step
		high = center + i*step
		if( (high - low) > width):
			break
		l.append(low)
		l.append(high)
	l.sort()
	return l

if __name__ == '__main__':
	gen = SweepGen()
	gen.freqList = freqRange(24000, 8000)
	# gen.start()

# gen.freqList = freqRange(24000, 8000) # easier to read VIF
# gen.freqList=freqRange(4500, 400, 10) # sif
# gen.freqList=freqRange(4500, 200, 10) # zoomed look at sif
