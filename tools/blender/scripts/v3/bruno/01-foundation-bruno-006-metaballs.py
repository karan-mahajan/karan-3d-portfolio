import bpy

def run():
    print('[06_metaballs] metaball datablocks')
    mb = bpy.data.metaballs.new('Mball.004')
    try: mb.resolution = 0.35999995470046997
    except Exception: pass
    try: mb.render_resolution = 0.20000000298023224
    except Exception: pass
    try: mb.threshold = 0.6000000238418579
    except Exception: pass
    try: mb.update_method = 'UPDATE_ALWAYS'
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (0.5533190965652466, 0.0715903639793396, -0.03404621034860611); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (0.9555031657218933, 0.4669915437698364, -0.12293365597724915); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-0.6682286858558655, 0.5281252264976501, -0.13235820829868317); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (0.9140225052833557, 0.4196271002292633, -0.947829008102417); el.radius = 0.8331866264343262; el.stiffness = 0.9062005877494812
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (0.8590056300163269, 0.7192431092262268, -3.2036960124969482); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-0.34342271089553833, 1.6811648607254028, -2.7261149883270264); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-0.7102229595184326, 1.5935845375061035, -1.836100459098816); el.radius = 0.8331866264343262; el.stiffness = 1.345394492149353
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-0.4758397340774536, 1.5380840301513672, -0.3741927742958069); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    mb.name = 'Mball.004'
    mb = bpy.data.metaballs.new('Mball.005')
    try: mb.resolution = 0.35999995470046997
    except Exception: pass
    try: mb.render_resolution = 0.20000000298023224
    except Exception: pass
    try: mb.threshold = 0.6000000238418579
    except Exception: pass
    try: mb.update_method = 'UPDATE_ALWAYS'
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (2.1973719596862793, 1.8189153671264648, -0.034046150743961334); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (1.6350544691085815, 1.5960848331451416, 0.3431274890899658); el.radius = 0.6557386517524719; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-4.106353282928467, 4.048703670501709, -0.13177257776260376); el.radius = 0.6653814911842346; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (2.64910888671875, 1.3324693441390991, -0.1242157369852066); el.radius = 1.0386641025543213; el.stiffness = 0.9062005877494812
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-0.8785776495933533, -0.004934318363666534, -5.5629987716674805); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-3.5226340293884277, 3.6431562900543213, -4.4479594230651855); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-4.727843761444092, 3.5983448028564453, -0.18661461770534515); el.radius = 0.8331866264343262; el.stiffness = 1.1576182842254639
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-2.0951619148254395, 2.956794023513794, -0.3741927146911621); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-2.997650146484375, 3.1231331825256348, -5.756214141845703); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-2.583946466445923, 4.713129997253418, -4.923170566558838); el.radius = 0.8331866264343262; el.stiffness = 6.03479528427124
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-2.4540250301361084, 3.9954962730407715, -5.414270401000977); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-1.0740147829055786, -0.4073059558868408, -4.874679088592529); el.radius = 0.8331866264343262; el.stiffness = 1.1855096817016602
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-4.864496231079102, -2.624866247177124, -5.606700420379639); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-5.183845043182373, -1.873018741607666, -5.606700420379639); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-5.1696696281433105, -1.4399149417877197, -5.606700420379639); el.radius = 0.8331866264343262; el.stiffness = 2.27726149559021
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (2.912590980529785, 2.366366386413574, -0.18207156658172607); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (2.8125832080841064, 2.938138961791992, -0.24570846557617188); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (1.342983365058899, 5.774880886077881, -0.41621920466423035); el.radius = 0.47708332538604736; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (1.9031563997268677, 5.978698253631592, -0.379772812128067); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (2.0561699867248535, 5.021341800689697, -0.8377207517623901); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (2.053055763244629, 5.140456676483154, -1.6096453666687012); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (2.327165126800537, 1.7899963855743408, -4.651917457580566); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (1.9683752059936523, 1.2940232753753662, -5.271763801574707); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (1.2597904205322266, 1.5056928396224976, -5.542826175689697); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (1.2123959064483643, 0.8100889921188354, -5.604955196380615); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (1.4293931722640991, 0.29174214601516724, -5.9470930099487305); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (1.490966558456421, 2.2291011810302734, -5.226247787475586); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-3.1072795391082764, 3.294475793838501, -0.4964550733566284); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (1.4107203483581543, 1.714812994003296, -0.5434130430221558); el.radius = 0.8331866264343262; el.stiffness = 1.0070064067840576
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-5.721396446228027, -3.0569241046905518, -6.128774642944336); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (3.0391950607299805, 4.928554058074951, -2.7957749366760254); el.radius = 0.8331866264343262; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (3.3626708984375, 5.713344573974609, -2.875166177749634); el.radius = 0.8331866264343262; el.stiffness = 1.3091042041778564
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (1.93074369430542, 5.713344573974609, -2.126971483230591); el.radius = 0.8331866264343262; el.stiffness = 1.236782193183899
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (0.3554578721523285, 2.083514928817749, -0.28209108114242554); el.radius = 0.8331866264343262; el.stiffness = 1.0070064067840576
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (0.544521152973175, 1.8439947366714478, -0.7646000981330872); el.radius = 0.8331866264343262; el.stiffness = 0.8443514704704285
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-4.27008581161499, 4.838069438934326, -0.2373526245355606); el.radius = 0.6653814911842346; el.stiffness = 2.0
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (1.1085538864135742, 5.5259480476379395, -0.22552090883255005); el.radius = 0.8331866264343262; el.stiffness = 1.1603541374206543
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    el = mb.elements.new(type='BALL')
    el.co = (-1.5257940292358398, 5.574688911437988, -0.2871219217777252); el.radius = 0.8331866264343262; el.stiffness = 1.5046066045761108
    try: el.rotation = (1.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: el.size_x = 1.0
    except Exception: pass
    try: el.size_y = 1.0
    except Exception: pass
    try: el.size_z = 1.0
    except Exception: pass
    try: el.use_negative = False
    except Exception: pass
    mb.name = 'Mball.005'

if __name__ == '__main__': run()