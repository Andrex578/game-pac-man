##############################################
# pacman_allinone.py - Pacman jogável completo
##############################################

import tkinter as tk
import random

CELL_SIZE = 30
MAP_WIDTH = 15
MAP_HEIGHT = 15
PACMAN_COLOR = 'yellow'
GHOST_COLOR = 'red'
FOOD_COLOR = 'white'
MOVE_DELAY = 100  # milissegundos entre movimentos

# ------------------------
# Classes básicas
# ------------------------
class Configuration:
    def __init__(self, pos):
        self.pos = pos
    def getPosition(self):
        return self.pos
    def setPosition(self,pos):
        self.pos = pos

class AgentState:
    def __init__(self,pos,isPacman):
        self.configuration = Configuration(pos)
        self.isPacman = isPacman

class Grid:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.data = [[False for _ in range(height)] for _ in range(width)]
    def __getitem__(self,i): return self.data[i]
    def __setitem__(self,key,item): self.data[key]=item
    def asList(self):
        lst=[]
        for x in range(self.width):
            for y in range(self.height):
                if self.data[x][y]:
                    lst.append((x,y))
        return lst

# ------------------------
# Display (Tkinter)
# ------------------------
class GraphicsDisplay:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.root = tk.Tk()
        self.root.title("Pacman")
        self.canvas = tk.Canvas(self.root,
                                width=self.width*CELL_SIZE,
                                height=self.height*CELL_SIZE,
                                bg='black')
        self.canvas.pack()
        self.pacman = None
        self.ghosts = []
        self.foodItems = []
        self.score_text = self.canvas.create_text(10,10, anchor='nw', fill='white', text="Score: 0")
    def drawPacman(self,pos):
        x,y = pos
        r=CELL_SIZE//2
        if self.pacman: self.canvas.delete(self.pacman)
        self.pacman = self.canvas.create_oval(x*CELL_SIZE+r//4,
                                             (self.height-1-y)*CELL_SIZE+r//4,
                                             (x+1)*CELL_SIZE-r//4,
                                             (self.height-y)*CELL_SIZE-r//4,
                                             fill=PACMAN_COLOR)
    def drawGhosts(self,ghosts):
        for g in self.ghosts: self.canvas.delete(g)
        self.ghosts = []
        for pos in ghosts:
            x,y = pos
            r=CELL_SIZE//2
            g = self.canvas.create_rectangle(x*CELL_SIZE+r//4,
                                             (self.height-1-y)*CELL_SIZE+r//4,
                                             (x+1)*CELL_SIZE-r//4,
                                             (self.height-y)*CELL_SIZE-r//4,
                                             fill=GHOST_COLOR)
            self.ghosts.append(g)
    def drawFood(self,foodList):
        for f in self.foodItems: self.canvas.delete(f)
        self.foodItems=[]
        for (x,y) in foodList:
            r=CELL_SIZE//4
            f=self.canvas.create_oval(x*CELL_SIZE+r,
                                      (self.height-1-y)*CELL_SIZE+r,
                                      (x+1)*CELL_SIZE-r,
                                      (self.height-y)*CELL_SIZE-r,
                                      fill=FOOD_COLOR)
            self.foodItems.append(f)
    def updateScore(self,score):
        self.canvas.itemconfig(self.score_text,text=f"Score: {score}")
    def update(self):
        self.root.update()

# ------------------------
# Game
# ------------------------
class PacmanGame:
    def __init__(self):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.display = GraphicsDisplay(self.width,self.height)
        self.food = Grid(self.width,self.height)
        # Colocar comida aleatória
        for x in range(self.width):
            for y in range(self.height):
                if random.random()<0.2: self.food[x][y]=True
        self.pacman = AgentState((self.width//2,self.height//2),True)
        self.pacman_dir = (0,0)
        self.score = 0
        # Fantasmas
        self.ghosts = [AgentState((1,1),False), AgentState((self.width-2,self.height-2),False)]
        self.display.root.bind("<KeyPress>",self.keyPressed)
        self.gameOver = False

    def keyPressed(self,event):
        if event.keysym in ['Up','w']: self.pacman_dir=(0,1)
        if event.keysym in ['Down','s']: self.pacman_dir=(0,-1)
        if event.keysym in ['Left','a']: self.pacman_dir=(-1,0)
        if event.keysym in ['Right','d']: self.pacman_dir=(1,0)

    def movePacman(self):
        x,y = self.pacman.configuration.getPosition()
        dx,dy = self.pacman_dir
        nx,ny = x+dx,y+dy
        if 0<=nx<self.width and 0<=ny<self.height:
            self.pacman.configuration.setPosition((nx,ny))
            if self.food[nx][ny]:
                self.food[nx][ny]=False
                self.score+=10

    def moveGhosts(self):
        pac_pos = self.pacman.configuration.getPosition()
        for ghost in self.ghosts:
            gx, gy = ghost.configuration.getPosition()
            px, py = pac_pos
            dx, dy = px - gx, py - gy

            move_options = []
            # Prioriza eixo com maior diferença
            if abs(dx) > abs(dy):
                move_options.append((1 if dx>0 else -1, 0))
                move_options.append((0, 1 if dy>0 else -1))
            else:
                move_options.append((0, 1 if dy>0 else -1))
                move_options.append((1 if dx>0 else -1, 0))
            move_options.append((0,0))  # ficar parado

            for mx, my in move_options:
                nx, ny = gx+mx, gy+my
                if 0<=nx<self.width and 0<=ny<self.height:
                    ghost.configuration.setPosition((nx,ny))
                    break

    def checkCollision(self):
        pac_pos = self.pacman.configuration.getPosition()
        for ghost in self.ghosts:
            if pac_pos == ghost.configuration.getPosition():
                self.gameOver = True
                print("GAME OVER!")

    def gameStep(self):
        if self.gameOver:
            return
        self.movePacman()
        self.moveGhosts()
        self.checkCollision()
        self.display.drawPacman(self.pacman.configuration.getPosition())
        self.display.drawGhosts([g.configuration.getPosition() for g in self.ghosts])
        self.display.drawFood(self.food.asList())
        self.display.updateScore(self.score)
        # chama a próxima atualização
        self.display.root.after(MOVE_DELAY, self.gameStep)

    def run(self):
        self.gameStep()
        self.display.root.mainloop()

# ------------------------
# Main
# ------------------------
if __name__=="__main__":
    game = PacmanGame()
    game.run()
