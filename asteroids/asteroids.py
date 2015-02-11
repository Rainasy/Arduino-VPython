from __future__ import division, print_function
from visual import *
import serial, sys, time, random

#gets data from Arduino
def getData():
    ser.write(chr(1))
    line = ser.readline()
    #print(line)
    data = line.split()
    LR = int(data[0])
    UD = int(data[1])
    BUTTON = int(data[2])
    #print(str(LR)+"\t"+str(UD))
    return [LR,UD,BUTTON]

#converts an angle in degrees to an angle in radians
def rad(degrees): 
    radians=degrees*pi/180
    return radians

#pause and wait for mouse or keyboard event, then continue
def pause():
    while True:
        rate(50)
        if scene.mouse.events:
            m = scene.mouse.getevent()
            if m.click == 'left': return
        elif scene.kb.keys:
            k = scene.kb.getkey()
            return

#checks for a collision between two spheres
def collisionSpheres(sphere1, sphere2):
    dist=mag(sphere1.pos-sphere2.pos)
    if(dist<sphere1.radius+sphere2.radius):
        return True
    else:
        return False

#checks for a collision between a cone and a sphere
def collisionConeSphere(c, s):

    #result is the variable that we will return
    #default is False
    result=False

    #check pos of cone
    if(collisionSphereAndPoint(s,c.pos)):
        result=True
    #check tip of cone
    result=False
    tip=c.pos+c.axis
    if(collisionSphereAndPoint(s,tip)):
        result=True
    #check edge of radius in x-y plane 1
    r1=c.radius*cross(vector(0,0,1),norm(c.axis))
    if(collisionSphereAndPoint(s,r1+c.pos)):
        result=True
    #check edge of radius in x-y plane 2
    r2=-c.radius*cross(vector(0,0,1),norm(c.axis))
    if(collisionSphereAndPoint(s,r2+c.pos)):
        result=True

    #return result
    return result

#determines whether a point is within a sphere or not
#returns boolean
def collisionSphereAndPoint(sphereObj, targetVector):
    dist=mag(sphereObj.pos-targetVector)
    if(dist<sphereObj.radius):
        return True
    else:
        return False
    
#creates four asteroids, one on each side of the scene
def createAsteroids():

    #asteroid comes from the right
    asteroid=sphere(pos=vector(20,0,0), radius=1, color=color.cyan)
    asteroid.pos.y=random.randrange(-20,20,5)
    asteroid.m=1
    asteroid.v=vector(0,0,0)
    asteroid.v.x=-random.randint(1,5)
    asteroid.v.y=random.choice((1,-1))*random.randint(1,5)
    asteroidList.append(asteroid)

    #asteroid comes from the left
    asteroid=sphere(pos=vector(-20,0,0), radius=1, color=color.cyan)
    asteroid.pos.y=random.randrange(-20,20,5)
    asteroid.m=1
    asteroid.v=vector(0,0,0)
    asteroid.v.x=random.randint(1,5)
    asteroid.v.y=random.choice((1,-1))*random.randint(1,5)
    asteroidList.append(asteroid)

    #asteroid comes from the top
    asteroid=sphere(pos=vector(0,20,0), radius=1, color=color.cyan)
    asteroid.pos.x=random.randrange(-20,20,5)
    asteroid.m=1
    asteroid.v=vector(0,0,0)
    asteroid.v.x=random.choice((1,-1))*random.randint(1,5)
    asteroid.v.y=-random.randint(1,5)
    asteroidList.append(asteroid)

    #asteroid comes from the bottom
    asteroid=sphere(pos=vector(0,-20,0), radius=1, color=color.cyan)
    asteroid.pos.x=random.randrange(-20,20,5)
    asteroid.m=1
    asteroid.v=vector(0,0,0)
    asteroid.v.x=random.choice((1,-1))*random.randint(1,5)
    asteroid.v.y=random.randint(1,5)
    asteroidList.append(asteroid)

def createFragments(asteroid):
    fragment1=sphere(pos=asteroid.pos, radius=0.5, color=color.magenta)
    fragment2=sphere(pos=asteroid.pos, radius=0.5, color=color.magenta)
    fragment1.m=0.5
    fragment2.m=0.5
    fragment1.v=vector(0,0,0)
    fragment1.v.x=random.choice((1,-1))*random.randint(1,5)
    fragment1.v.y=random.choice((1,-1))*random.randint(1,5)
    fragment2.v=2*asteroid.v-fragment1.v
    fragmentList.append(fragment1)
    fragmentList.append(fragment2)   

#set serial port
port = '/dev/cu.usbmodem1421'

#start the serial port
ser = serial.Serial(port, 9600, timeout=2)

# The following line is necessary to give the arduino time to start
# accepting stuff.
time.sleep(2)


#scene size
scene.range=20
scene.width=700
scene.height=700

#create the spaceship as a cone
spaceship = cone(pos=(0,0,0), axis=(2,0,0), radius=1, color=color.white)
fire = cone(pos=(0,0,0), axis=-spaceship.axis/2, radius=spaceship.radius/2, color=color.orange)

#initial values for mass, velocity
spaceship.m=1
spaceship.v=vector(0,0,0)

#bullets
bulletspeed=10
bulletsList=[]

#angle to rotate
dtheta=rad(10)

#clock
t=0
dt=0.01

#asteroids
Nleft=0 #counter for number of asteroids left in the scene
asteroidList=[]
createAsteroids()

#fragments
fragmentList=[]

#voltage from Arduino
voltage=[]
#scale factor for voltage
scale=10 
#force from voltage
F=vector(0,0,0)
#If F is less than this value, set it to zero
Fmin=scale*0.2

while spaceship.visible==1:
    rate(100)

    voltage=getData()
    F.x=scale*(voltage[0]-1023/2)/512
    F.y=scale*(voltage[1]-1023/2)/512
    fireBullet=voltage[2]
    if(fireBullet):
#        print(voltage)
		bullet=sphere(pos=spaceship.pos+spaceship.axis, radius=0.1, color=color.yellow)
		bullet.v=bulletspeed*norm(spaceship.axis)+spaceship.v
		bulletsList.append(bullet)


    if(mag(F)>Fmin):
        spaceship.axis=norm(F)

# 	if scene.kb.keys:
# 		k = scene.kb.getkey()
# 		if k==" ": #fire a bullet
# 			bullet=sphere(pos=spaceship.pos+spaceship.axis, radius=0.1, color=color.yellow)
# 			bullet.v=bulletspeed*norm(spaceship.axis)+spaceship.v
# 			bulletsList.append(bullet)
# 		elif k=="q": #pause the game
# 			pause()


    spaceship.v=spaceship.v+F/spaceship.m*dt
    spaceship.pos=spaceship.pos+spaceship.v*dt
    fire.pos=spaceship.pos
    fire.axis=-spaceship.axis/2


    #check if the spaceship goes off screen and wrap
    if spaceship.pos.x>20 or spaceship.pos.x<-20:
        spaceship.pos=spaceship.pos-spaceship.v*dt
        spaceship.pos.x=-spaceship.pos.x
    if spaceship.pos.y>20 or spaceship.pos.y<-20:
        spaceship.pos=spaceship.pos-spaceship.v*dt
        spaceship.pos.y=-spaceship.pos.y

    #update positions of bullets and check if bullets go off screen
    for thisbullet in bulletsList:
        if thisbullet.pos.x>20 or thisbullet.pos.x<-20:
            thisbullet.visible=0
        if thisbullet.pos.y>20 or thisbullet.pos.y<-20:
            thisbullet.visible=0
        if thisbullet.visible != 0:
            thisbullet.pos=thisbullet.pos+thisbullet.v*dt

    #update positions of asteroids
    for thisasteroid in asteroidList:
        if thisasteroid.visible==1:
            thisasteroid.pos=thisasteroid.pos+thisasteroid.v*dt
            #check for collision with spaceship
            if(collisionConeSphere(spaceship,thisasteroid)):
                spaceship.visible=0
                fire.visible=0
            #wrap at edge of screen
            if thisasteroid.pos.x>20 or thisasteroid.pos.x<-20:
                thisasteroid.pos=thisasteroid.pos-thisasteroid.v*dt
                thisasteroid.pos.x=-thisasteroid.pos.x
            if thisasteroid.pos.y>20 or thisasteroid.pos.y<-20:
                thisasteroid.pos=thisasteroid.pos-thisasteroid.v*dt
                thisasteroid.pos.y=-thisasteroid.pos.y
            #check for collision with bullets
            for thisbullet in bulletsList:
                if(collisionSpheres(thisbullet,thisasteroid)and thisbullet.visible==1):
                   thisasteroid.visible=0
                   thisbullet.visible=0
                   createFragments(thisasteroid)

    #update positions of fragments
    for thisfragment in fragmentList:
        if thisfragment.visible==1:
            thisfragment.pos=thisfragment.pos+thisfragment.v*dt
            #check for collision with spaceship
            if(collisionConeSphere(spaceship,thisfragment)):
                spaceship.visible=0
                fire.visible=0
            #wrap at edge of screen
            if thisfragment.pos.x>20 or thisfragment.pos.x<-20:
                thisfragment.pos=thisfragment.pos-thisfragment.v*dt
                thisfragment.pos.x=-thisfragment.pos.x
            if thisfragment.pos.y>20 or thisfragment.pos.y<-20:
                thisfragment.pos=thisfragment.pos-thisfragment.v*dt
                thisfragment.pos.y=-thisfragment.pos.y
            #check for collision with bullets
            for thisbullet in bulletsList:
                if(collisionSpheres(thisbullet,thisfragment)and thisbullet.visible==1):
                   thisfragment.visible=0
                   thisbullet.visible=0


    Nleft=0 #have to reset this before counting asteroids and fragments
    for thisasteroid in asteroidList:
        if thisasteroid.visible:
            Nleft=Nleft+1
    for thisfragment in fragmentList:
        if thisfragment.visible:
            Nleft=Nleft+1

    #create more asteroids if all are gone
    if Nleft==0:
        createAsteroids()

    #update fire
    if mag(F)<Fmin or spaceship.visible==0:
        fire.visible=0
    else:
        fire.visible=1

    t=t+dt
