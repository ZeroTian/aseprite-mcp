"""Reusable Lua snippets shared by tool modules.

These are embedded at the top of generated batch scripts. Scripts built
with them should print "ERROR:<message>" to signal failure and be run
through AsepriteCommand.execute_lua_script_checked.
"""

# Find a top-level layer by name (same convention as the rest of the
# codebase: groups are not traversed).
FIND_LAYER = """
local function find_layer(spr, name)
    for _, layer in ipairs(spr.layers) do
        if layer.name == name then return layer end
    end
    return nil
end
"""

# Replace a cel's image with a canvas-sized image anchored at (0,0) so
# sprite-global coordinates can be used directly without cel offsets.
NORMALIZE_CEL = """
local function normalize_cel(spr, layer, frame, create)
    local cel = layer:cel(frame)
    if not cel then
        if not create then return nil end
        local img = Image(spr.width, spr.height, spr.colorMode)
        return spr:newCel(layer, frame, img, Point(0, 0))
    end
    if cel.position.x == 0 and cel.position.y == 0
       and cel.image.width == spr.width and cel.image.height == spr.height then
        return cel
    end
    local img = Image(spr.width, spr.height, spr.colorMode)
    img:drawImage(cel.image, cel.position)
    cel.image = img
    cel.position = Point(0, 0)
    return cel
end
"""

# Bounds-guarded putPixel.
PSET = """
local function pset(img, x, y, color)
    if x >= 0 and y >= 0 and x < img.width and y < img.height then
        img:putPixel(x, y, color)
    end
end
"""

# RGB <-> HSL conversion. h in [0,360), s and l in [0,1].
HSL = """
local function rgb_to_hsl(r, g, b)
    r, g, b = r / 255, g / 255, b / 255
    local maxc = math.max(r, g, b)
    local minc = math.min(r, g, b)
    local l = (maxc + minc) / 2
    if maxc == minc then return 0, 0, l end
    local d = maxc - minc
    local s
    if l > 0.5 then s = d / (2 - maxc - minc) else s = d / (maxc + minc) end
    local h
    if maxc == r then
        h = (g - b) / d
        if g < b then h = h + 6 end
    elseif maxc == g then
        h = (b - r) / d + 2
    else
        h = (r - g) / d + 4
    end
    return h * 60, s, l
end

local function hsl_to_rgb(h, s, l)
    h = h % 360
    if s <= 0 then
        local v = math.floor(l * 255 + 0.5)
        return v, v, v
    end
    local c = (1 - math.abs(2 * l - 1)) * s
    local hp = h / 60
    local x = c * (1 - math.abs(hp % 2 - 1))
    local r1, g1, b1 = 0, 0, 0
    if hp < 1 then r1, g1, b1 = c, x, 0
    elseif hp < 2 then r1, g1, b1 = x, c, 0
    elseif hp < 3 then r1, g1, b1 = 0, c, x
    elseif hp < 4 then r1, g1, b1 = 0, x, c
    elseif hp < 5 then r1, g1, b1 = x, 0, c
    else r1, g1, b1 = c, 0, x end
    local m = l - c / 2
    return math.floor((r1 + m) * 255 + 0.5),
           math.floor((g1 + m) * 255 + 0.5),
           math.floor((b1 + m) * 255 + 0.5)
end
"""
