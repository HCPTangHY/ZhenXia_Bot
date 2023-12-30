import pandas,os,math,sqlite3
from PIL import Image,ImageDraw,ImageFont
from .models import Star,Country

RES_X = 384 + 1
RES_Y = 384 + 1
MAP_WIDTH = 1000
MAP_HEIGHT = 1000
UNOWNED_VALUE = 20
UNOWNED_RADIUS = 110
UNOWNED_HYPERLANE_RADIUS = 95
SYSTEM_RADIUS = UNOWNED_RADIUS + UNOWNED_VALUE - 6
HYPERLANE_RADIUS = UNOWNED_HYPERLANE_RADIUS + UNOWNED_VALUE - 6
PADDING = 50
INNER_PADDING = 10
PAINT_SCALE_FACTOR = 2
NEAR_RADIUS = 20
NEAR_BOOST = 100
ENTRIES_KEY = '___entries'
UNOWNED_ID = -1000000000

def get_map(stars, hyperlanes, scaleFactor, sizeX, sizeY):
    map_data = []
    for i in range(RES_X):
        column = []
        for j in range(RES_Y):
            obj = {UNOWNED_ID: scaleFactor * UNOWNED_VALUE}
            column.append(obj)
        map_data.append(column)

    for id,star in stars.items():
        baseRadius = SYSTEM_RADIUS
        owner = star['owner']
        if owner is None:
            owner = UNOWNED_ID
            baseRadius = UNOWNED_RADIUS
        else:
            owner = owner

        baseRadius *= scaleFactor
        imin = max(0, int((star['x'] - baseRadius) / sizeX))
        imax = min(RES_X, int((star['x'] + baseRadius) / sizeX))
        jmin = max(0, int((star['y'] - baseRadius) / sizeY))
        jmax = min(RES_Y, int((star['y'] + baseRadius) / sizeY))

        for i in range(imin, imax):
            for j in range(jmin, jmax):
                x = sizeX * i
                y = sizeY * j
                distance = ((star['x'] - x) ** 2 + (star['y'] - y) ** 2) ** 0.5
                value = baseRadius - distance
                if distance < NEAR_RADIUS * scaleFactor:
                    value -= baseRadius - NEAR_RADIUS * scaleFactor
                    value *= NEAR_BOOST
                    value += baseRadius - NEAR_RADIUS * scaleFactor
                value = max(0, value)
                if column := map_data[i][j]:
                    if column.get(owner) is None:
                        column[owner] = 0
                    column[owner] = max(column[owner], value)
    for key, hyperlane in hyperlanes.items():
        if stars[hyperlane['from']]['owner'] != stars[hyperlane['to']]['owner']:
            continue

        baseRadius = HYPERLANE_RADIUS
        owner = stars[hyperlane['from']]['owner']
        if owner is None:
            owner = UNOWNED_ID
            baseRadius = UNOWNED_HYPERLANE_RADIUS
        else:
            owner = owner

        baseRadius *= scaleFactor
        x1 = stars[hyperlane['from']]['x']
        y1 = stars[hyperlane['from']]['y']
        x2 = stars[hyperlane['to']]['x']
        y2 = stars[hyperlane['to']]['y']

        a = y1 - y2
        b = x2 - x1
        c = a * x1 + b * y1
        x3 = x1 - (y2 - y1)
        y3 = y1 + (x2 - x1)
        distanceFactor = ((x3 - x1) ** 2 + (y3 - y1) ** 2) ** 0.5 / abs(a * x3 + b * y3 - c)

        a2 = b
        b2 = -a
        c2 = a2 * ((x1 + x2) / 2) + b2 * ((y1 + y2) / 2)
        halfLength = abs(a2 * x1 + b2 * y1 - c2)

        imin = max(0, int((min(x1, x2) - baseRadius) / sizeX))
        imax = min(RES_X, int((max(x1, x2) + baseRadius) / sizeX))
        jmin = max(0, int((min(y1, y2) - baseRadius) / sizeY))
        jmax = min(RES_Y, int((max(y1, y2) + baseRadius) / sizeY))
        for i in range(imin, imax):
            column = map_data[i]
            for j in range(jmin, jmax):
                x = sizeX * i
                y = sizeY * j
                distance = min(((x - x1) ** 2 + (y - y1) ** 2) ** 0.5, ((x - x2) ** 2 + (y - y2) ** 2) ** 0.5)
                if abs(a2 * x + b2 * y - c2) <= halfLength:
                    distance = min(distance, distanceFactor * abs(a * x + b * y - c))
                value = baseRadius - distance
                if distance < NEAR_RADIUS / 2  * scaleFactor:
                    value -= baseRadius - NEAR_RADIUS / 2 * scaleFactor
                    value *= NEAR_BOOST / 2
                    value += baseRadius - NEAR_RADIUS / 2 * scaleFactor
                value = max(0, value)
                if not math.isfinite(value):
                    continue
                if column[j].get(owner) is None:
                    column[j][owner] = 0
                column[j][owner] = max(column[j][owner], value)
    return map_data

def draw_country_fill(draw,colors, map, values, sizeX, sizeY):
    for currentId in colors:
        if currentId == UNOWNED_ID:
            continue
        fill_color = colors[currentId]+"66" or (0,0,0)
        for j in range(RES_Y - 1):
            for i in range(RES_X - 1):
                value_UL = values[i][j]
                value_UR = values[i + 1][j]
                value_BL = values[i][j + 1]
                value_BR = values[i + 1][j + 1]

                if value_UL['id'] != currentId and value_UR['id'] != currentId and value_BL['id'] != currentId and value_BR['id'] != currentId:
                    continue

                xmin = sizeX * i
                xmax = xmin + sizeX
                ymin = sizeY * j
                ymax = ymin + sizeY

                UL = map[i][j]
                UR = map[i + 1][j]
                BL = map[i][j + 1]
                BR = map[i + 1][j + 1]

                if value_UL['id'] == value_UR['id'] and value_UR['id'] == value_BL['id'] and value_BL['id'] == value_BR['id']:
                    if value_UL['id'] != currentId:
                        continue
                    draw.rectangle([xmin, ymin, xmax, ymax], fill=fill_color)
                    continue
def draw_star(draw,stars:list[Star],colors):
    for i in range(len(stars)):
        stars[i].x*=2.75
        stars[i].x+=150
        stars[i].y*=2.75
        stars[i].y+=20
    for s in stars:
        for t in s.hyperlane:
            target = Star.search_by_id(t)
            if target.id==0:continue
            else:
                target.x*=2.75
                target.x+=150
                target.y*=2.75
                target.y+=20
                draw.line(((s.x,s.y),(target.x,target.y)),(0,245,255),width=3)
    for s in stars:
        draw.ellipse(((s.x-15,s.y-15),(s.x+15,s.y+15)),fill=colors[s.owner],outline=colors[s.controller],width=5)
        draw.text((s.x-((len(s.name)/2)*10),s.y+15),text=f"{s.name}\n{s.id}",fill=(255,255,255),font=ImageFont.truetype("simhei",10,encoding='utf-8'))
def generate_map(allStar:list[Star]):
    stars = {}
    hyperlanes = {}
    xmin = math.inf
    xmax = -math.inf
    ymin = math.inf
    ymax = -math.inf
    innerRadius = math.inf
    for star in allStar:
        id = int(star.id)

        xmin = min(xmin, float(star.x))
        xmax = max(xmax, float(star.x))
        ymin = min(ymin, float(star.y))
        ymax = max(ymax, float(star.y))

        innerRadius = min(innerRadius, ((float(star.x) ** 2) + (float(star.y) ** 2)) ** 0.5)
        stars[id] = {
            'x': (float(star.x*2.75+150)),
            'y': float(star.y*2.75+20),
            'owner': star.owner,
            'hyperlanes': not (star.hyperlane is None or len(star.hyperlane) == 0),
            'id': id
        }
        if star.hyperlane is not None:
            for hyperlaneStar in star.hyperlane:
                from_id = id
                to_id = int(hyperlaneStar)
                if to_id not in stars:continue

                if from_id > to_id:
                    from_id, to_id = to_id, from_id
                key = f"{from_id},{to_id}"
                hyperlanes[key] = {
                    'from': from_id,
                    'to': to_id
                }
    colors = {}
    countrys:list[Country] = Country.get_all_country()
    for c in countrys:
        colors[c.tag]=c.color

    sizeX = MAP_WIDTH / (RES_X - 1)
    sizeY = MAP_HEIGHT / (RES_Y - 1)

    scale = min(
        (MAP_WIDTH / 2 - (SYSTEM_RADIUS - UNOWNED_VALUE) - PADDING) / max(abs(xmax), abs(xmin)),
        (MAP_HEIGHT / 2 - (SYSTEM_RADIUS - UNOWNED_VALUE) - PADDING) / max(abs(ymax), abs(ymin))
    )

    innerRadius = max(0, min(MAP_WIDTH, MAP_HEIGHT, scale * innerRadius - INNER_PADDING))

    scaleFactor = scale / PAINT_SCALE_FACTOR

    map_data = get_map(stars, hyperlanes, scaleFactor, sizeX, sizeY)
    # if SMOOTH_BORDERS:
    #     map_data = smoothMap(map_data)

    values = []
    for i in range(RES_X):
        column = []
        for j in range(RES_Y):
            value = {'id': UNOWNED_ID, 'value': 0}
            for id, val in map_data[i][j].items():
                if val > value['value']:
                    value['id'] = id
                    value['value'] = val
            column.append(value)
        values.append(column)
    image = Image.new("RGB", (1000,1000))
    draw = ImageDraw.Draw(image)
    draw_country_fill(draw,colors,map_data,values,sizeX,sizeY)
    mapImg = Image.new("RGB", (1000,1000))
    mapImg = Image.blend(mapImg,image,0.5)
    draw = ImageDraw.Draw(mapImg)
    draw_star(draw,allStar,colors)
    
    return mapImg
# generate_map(Star.get_all_stars())
