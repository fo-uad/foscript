from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

block_pick = 1
arm = None
player = None
creative_mode = False  # start in survival mode
command_line_active = False
command_line = None
inventory_ui = None
blocks_positions = []  # moved to global for access inside Voxel


def run_minecraft():
    global block_pick, arm, player, creative_mode, command_line, command_line_active, inventory_ui, blocks_positions

    app = Ursina()

    # Load assets with fallbacks to built-in ones if not found
    try:
        grass_texture = load_texture('assets/grass.png')
    except:
        print('Failed to load grass.png, using default')
        grass_texture = 'white_cube'

    try:
        dirt_texture = load_texture('assets/dirt.png')
    except:
        print('Failed to load dirt.png, using default')
        dirt_texture = 'white_cube'

    try:
        stone_texture = load_texture('assets/stone.png')
    except:
        print('Failed to load stone.png, using default')
        stone_texture = 'white_cube'

    try:
        sky_texture = load_texture('assets/skybox.png')
    except:
        print('Failed to load skybox.png, using default')
        sky_texture = 'sky_sunset'

    try:
        arm_texture = load_texture('assets/arm_texture.png')
    except:
        print('Failed to load arm_texture.png, using default')
        arm_texture = 'white_cube'

    # For models, fallback to built-in cube/quad if missing
    import os
    block_model = 'assets/block.obj' if os.path.isfile('assets/block.obj') else 'cube'
    arm_model = 'assets/arm.obj' if os.path.isfile('assets/arm.obj') else 'cube'

    player = FirstPersonController()
    player.gravity = 1  # gravity ON by default (survival mode)
    player.speed = 5
    player.cursor.visible = True

    window.fps_counter.enabled = True
    window.exit_button.visible = False

    blocks_positions.clear()  # ensure empty before generating

    class Voxel(Button):
        def __init__(self, position=(0,0,0), texture=grass_texture):
            super().__init__(
                parent=scene,
                position=position,
                model=block_model,
                origin_y=0.5,
                texture=texture,
                color=color.color(0, 0, random.uniform(0.9, 1.0)),
                scale=1
            )
            # Track grass blocks for spawn position
            if texture == grass_texture:
                blocks_positions.append(position)

        def input(self, key):
            global block_pick
            if self.hovered:
                if key == 'left mouse down':
                    destroy(self)
                if key == 'right mouse down':
                    if block_pick == 1:
                        Voxel(position=self.position + mouse.normal, texture=grass_texture)
                    elif block_pick == 2:
                        Voxel(position=self.position + mouse.normal, texture=stone_texture)
                    elif block_pick == 3:
                        Voxel(position=self.position + mouse.normal, texture=dirt_texture)

    class Sky(Entity):
        def __init__(self):
            super().__init__(
                parent=scene,
                model='sphere',
                texture=sky_texture,
                scale=150,
                double_sided=True
            )

    arm = Entity(
        parent=camera.ui,
        model=arm_model,
        texture=arm_texture,
        scale=0.2,
        rotation=Vec3(150, -10, 0),
        position=Vec2(0.6, -0.6)
    )

    globals()['arm'] = arm

    def generate_chunk(offset_x=0, offset_z=0):
        for x in range(16):
            for z in range(16):
                world_x = x + offset_x
                world_z = z + offset_z
                height = random.randint(3, 8)

                for y in range(height - 2):
                    Voxel(position=(world_x, y, world_z), texture=stone_texture)
                Voxel(position=(world_x, height - 2, world_z), texture=dirt_texture)
                Voxel(position=(world_x, height - 1, world_z), texture=grass_texture)

    generate_chunk()

    Sky()

    # Place player on surface (highest grass block)
    if blocks_positions:
        highest_block = max(blocks_positions, key=lambda pos: pos[1])  # pos is tuple (x,y,z)
        # pos[0]=x, pos[1]=y, pos[2]=z
        player.position = Vec3(highest_block[0], highest_block[1] + 2, highest_block[2])
    else:
        player.position = (0, 10, 0)  # fallback spawn

    # Inventory UI (simple text showing current block)
    inventory_ui = Text(
        text=f'Block selected: {block_pick} (1=Grass, 2=Stone, 3=Dirt)',
        position=window.top_left + Vec2(0.05, -0.05),
        origin=(0, 0),
        scale=2,
        background=True
    )
    globals()['inventory_ui'] = inventory_ui

    # Command line input (hidden by default)
    command_line = InputField(
        parent=camera.ui,
        scale_x=0.5,
        scale_y=0.04,
        y=-0.4,
        active=False,
        text='',
        placeholder='Type command and press Enter...',
    )

    globals()['command_line'] = command_line

    def on_submit():
        global creative_mode, command_line_active, player, command_line

        cmd = command_line.text.strip().lower()
        if cmd.startswith('/gamemode '):
            mode = cmd[len('/gamemode '):].strip()
            if mode in ('creative', 'c'):
                creative_mode = True
                player.gravity = 0
                print('Switched to Creative mode.')
            elif mode in ('survival', 's'):
                creative_mode = False
                player.gravity = 1
                print('Switched to Survival mode.')
            else:
                print(f'Unknown gamemode: {mode}')
        else:
            print(f'Unknown command: {cmd}')
        command_line.text = ''
        command_line.active = False
        command_line_active = False
        mouse.locked = True  # re-lock mouse for gameplay

    command_line.on_submit = on_submit

    def input_handler(key):
        global command_line_active, command_line

        if key == '/':
            if not command_line_active:
                command_line.active = True
                command_line_active = True
                mouse.locked = False
                command_line.focus()
        elif key == 'enter':
            if command_line_active:
                command_line.on_submit()
        elif key == 'escape' and command_line_active:
            command_line.text = ''
            command_line.active = False
            command_line_active = False
            mouse.locked = True

    app.input = input_handler

    app.run()


def update():
    global block_pick, arm, player, creative_mode, inventory_ui

    if held_keys['1']:
        block_pick = 1
    if held_keys['2']:
        block_pick = 2
    if held_keys['3']:
        block_pick = 3

    # Update inventory UI text
    if inventory_ui:
        inventory_ui.text = f'Block selected: {block_pick} (1=Grass, 2=Stone, 3=Dirt)'

    if player:
        if creative_mode:
            if held_keys['space']:
                player.y += time.dt * 5
            if held_keys['left shift'] or held_keys['shift']:
                player.y -= time.dt * 5

    if arm:
        if held_keys['left mouse'] or held_keys['right mouse']:
            arm.rotation_z = 30
        else:
            arm.rotation_z = 0