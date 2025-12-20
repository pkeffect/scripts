import numpy as np
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

# --- Constants ---
WIDTH, HEIGHT = 1280, 720

# --- Helper Function to Load Textures ---
def load_texture(path):
    """Loads an image file and returns an OpenGL texture ID."""
    try:
        img = Image.open(path).convert("RGBA")
        img_data = np.array(list(img.getdata()), np.uint8)

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        # Texture parameters for wrapping and filtering
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        
        print(f"Texture '{path}' loaded successfully.")
        return texture_id
    except FileNotFoundError:
        print(f"Error: Texture file not found at '{path}'")
        return None

# --- Celestial Body Classes ---
class Earth:
    def __init__(self):
        self.radius = 1.0
        self.position = np.array([0.0, 0.0, 0.0]) # Centered at the origin
        self.rotation_angle = 0.0
        self.rotation_speed = 0.2 # Degrees per frame
        self.quadric = gluNewQuadric()
        self.texture_id = load_texture("earth.jpg")

    def draw(self):
        glPushMatrix()
        
        # Apply Earth's rotation on its axis
        glRotatef(self.rotation_angle, 0, 1, 0) # Rotate around Y-axis for a natural spin

        # Enable texturing
        if self.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            gluQuadricTexture(self.quadric, GL_TRUE)
        
        # Set material color (will be multiplied by texture color)
        glColor3f(1.0, 1.0, 1.0)
        
        # Draw the sphere
        gluSphere(self.quadric, self.radius, 64, 32)
        
        # Clean up
        if self.texture_id:
            glDisable(GL_TEXTURE_2D)
            
        glPopMatrix()

    def update(self):
        self.rotation_angle += self.rotation_speed
        if self.rotation_angle >= 360:
            self.rotation_angle -= 360

class Moon:
    def __init__(self, earth_obj):
        self.earth = earth_obj
        self.radius = 0.27 # To scale with Earth's radius
        self.orbit_radius = 3.5
        self.orbit_angle = 0.0
        self.orbit_speed = 1.0 # Degrees per frame
        self.position = np.array([0.0, 0.0, 0.0]) # Position will be calculated in update
        self.quadric = gluNewQuadric()
        self.texture_id = load_texture("moon.jpg")
        self.update() # Set initial position

    def draw(self):
        glPushMatrix()
        
        # Move the moon to its calculated position
        glTranslatef(*self.position)
        
        # Enable texturing
        if self.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            gluQuadricTexture(self.quadric, GL_TRUE)
        
        glColor3f(1.0, 1.0, 1.0)
        
        # Draw the sphere
        gluSphere(self.quadric, self.radius, 32, 16)
        
        # Clean up
        if self.texture_id:
            glDisable(GL_TEXTURE_2D)

        glPopMatrix()

    def update(self):
        # Update orbit angle
        self.orbit_angle += self.orbit_speed
        if self.orbit_angle >= 360:
            self.orbit_angle -= 360
            
        # Recalculate position based on the new angle and Earth's position
        angle_rad = np.radians(self.orbit_angle)
        x = self.earth.position[0] + self.orbit_radius * np.cos(angle_rad)
        z = self.earth.position[2] + self.orbit_radius * np.sin(angle_rad) # Orbit in the XZ plane
        self.position = np.array([x, 0, z])

    def draw_orbit(self):
        """Draws a line representing the Moon's orbital path."""
        glBegin(GL_LINE_LOOP)
        glColor3f(0.5, 0.5, 0.5) # Faint grey for the orbit line
        for i in range(360):
            angle_rad = np.radians(i)
            x = self.earth.position[0] + self.orbit_radius * np.cos(angle_rad)
            z = self.earth.position[2] + self.orbit_radius * np.sin(angle_rad)
            glVertex3f(x, 0, z)
        glEnd()

# --- Main Application ---
def setup_opengl():
    """Sets up the initial OpenGL state."""
    glClearColor(0.0, 0.0, 0.05, 1.0) # Dark blue background
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Set up light properties
    glLightfv(GL_LIGHT0, GL_POSITION, (5, 5, 5, 1)) # Light position
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))

    # Set up the projection matrix (the camera lens)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (WIDTH / HEIGHT), 0.1, 50.0)

    # Switch back to the model view matrix
    glMatrixMode(GL_MODELVIEW)

def main():
    pygame.init()
    display = (WIDTH, HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Earth and Moon Simulation | Drag to Rotate, Scroll to Zoom")
    
    setup_opengl()
    
    clock = pygame.time.Clock()

    # Create celestial objects
    earth = Earth()
    moon = Moon(earth)

    # Camera control variables
    zoom = -10
    rotation_x = 30
    rotation_y = 0
    last_mouse_pos = None
    is_mouse_down = False

    # --- Main Loop ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
            
            # Mouse controls for camera
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    is_mouse_down = True
                    last_mouse_pos = event.pos
                elif event.button == 4: # Scroll up
                    zoom = max(-20, zoom + 0.5)
                elif event.button == 5: # Scroll down
                    zoom = min(-5, zoom - 0.5)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    is_mouse_down = False

            elif event.type == MOUSEMOTION:
                if is_mouse_down:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    rotation_y += dx * 0.2
                    rotation_x += dy * 0.2
                    last_mouse_pos = event.pos

        # Update object states
        earth.update()
        moon.update()

        # Drawing
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Apply camera transformations
        glTranslatef(0.0, 0.0, zoom)
        glRotatef(rotation_x, 1, 0, 0)
        glRotatef(rotation_y, 0, 1, 0)
        
        # Draw all objects
        earth.draw()
        moon.draw()
        moon.draw_orbit()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()