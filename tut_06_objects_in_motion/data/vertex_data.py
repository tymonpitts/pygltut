NUMBER_OF_VERTICES = 8

_COLOR = {"GREEN" : [0.0,1.0,0.0,1.0],
          "BLUE"  : [0.0,0.0,1.0,1.0],
          "RED"   : [1.0,0.0,0.0,1.0],
          "GREY"  : [0.8,0.8,0.8,1.0],
          "BROWN" : [0.5,0.5,0.0,1.0]}

_POSITIONS = [ 1.0, 1.0, 1.0,
              -1.0,-1.0, 1.0,
              -1.0, 1.0,-1.0,
               1.0,-1.0,-1.0,

              -1.0,-1.0,-1.0,
               1.0, 1.0,-1.0,
               1.0,-1.0, 1.0,
              -1.0, 1.0, 1.0]

_COLORS = (_COLOR["GREEN"]+_COLOR["BLUE"]+_COLOR["RED"]+_COLOR["BROWN"])*2

VERTEX_DATA = _POSITIONS+_COLORS

INDICES = [0,1,2,
           1,0,3,
           2,3,0,
           3,2,1,

           5,4,6,
           4,5,7,
           7,6,4,
           6,7,5]