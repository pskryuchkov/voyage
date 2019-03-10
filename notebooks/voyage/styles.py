import plotly.graph_objs as go


class CityMapStyle:
    MARKER_SIZE = 17
    MARKER_OPACITY = 0.4
    MARKER_COLOR = 'red'
    ZOOM = 12
    MAP_WIDTH = 800
    MAP_HEIGHT = 470
    MAX_MARKER_SIZE = 40
    MIN_MARKER_SIZE = 3
    MIN_LOCATIONS = 15
    MARGIN = dict(l=0, r=30, b=0, t=20)


class StreetAreaCombine:
    HOLE = 0.5
    PULL = 0.05
    PIE_AREA_X = [0.1, 1.0]
    PIE_AREA_Y = [0.2, 0.8]
    BAR_CHART_OPACITY = 0.8
    BAR_CHART_COLOR = 'red'
    BAR_CHART_CM = "Wistia"
    BAR_CHART_LEGEND_X = 0.55
    BAR_CHART_LEGEND_Y = 0.0
    
    TICK_LEN = 4
    PLOT_HEIGHT = 350
    PLOT_WIDTH = 900
    BAR_CHART_AREA_X = [0, 0.25]
    BAR_CHART_AREA_Y = [0, 1.0]
    MARGIN = go.layout.Margin(l=220, t=15, b=15, r=0)
    
    BAR_CHART_FONT_COLOR = 'lightgrey'
    BAR_CHART_FONT_SIZE = 11
    PIE_CHART_FONT_COLOR = 'grey'
    PIE_CHART_FONT_SIZE = 11
    
    MIN_COLOR_VALUE = 0.20
    MAX_COLOR_VALUE = 0.60 


class InstaWikiScatterStyle:
    PLOT_HEIGHT = 400
    PLOT_WIDTH = 550
    MARKER_OPACITY = 0.8
    MARKER_COLOR = 'dodgerblue'
    FONT_COLOR = 'lightgrey'
    FONT_SIZE = 8
    LINE_STYLE = 'dash'
    LINE_COLOR = 'grey'
    LINE_WIDTH = 2
    AXES_TYPE = 'log'
    MARGIN = go.layout.Margin(t=30, b=50, l=50, r=30)


class FaceScatterStyle:
    MIN_X = -0.02
    MAX_X = 0.8
    PLOT_HEIGHT = 420
    PLOT_WIDTH = 600
    FONT_SIZE = 11
    FONT_COLOR = 'lightgrey'
    MARKER_COLOR = 'dodgerblue'
    MARKER_OPACITY = 0.25
    MARKER_SIZE = 8
    MEDIAN_MARKER_SIZE = 7
    MEDIAN_MARKER_OPACITY = 0.9
    MEDIAN_MARKER_COLOR = 'darkblue' 
    MEDIAN_MARKER_SYMBOL = 'x-thin-open'
    MEDIAN_LINEWIDTH = 1.8
    MARGIN = dict(l=150, r=30, b=20, t=20)


class TagsRateStyle:
    FONT_SIZE = 11.5
    PLOT_WIDTH = 550
    PLOT_HEIGHT = 330
    OPACITY = 0.9
    VERTICAL_SPACING = 0.15
    RATE_BAR_COLOR = 'red'
    TICKFONT_COLOR = 'lightgrey'
    MARGIN = go.layout.Margin(t=30, b=120, l=30, r=25)


class TagsDeltaStyle:
    FONT_SIZE = 11.5
    PLOT_WIDTH = 550
    PLOT_HEIGHT = 330
    VERTICAL_SPACING = 0.15
    DELTA_BAR_COLOR = 'dodgerblue'
    TICKFONT_COLOR = 'lightgrey'
    OPACITY = 0.9
    MARGIN = go.layout.Margin(t=30, b=120, l=30, r=25)


class StreetsFeaturesPlotStyle:
    FONT_SIZE = 11
    MAX_IM_VALUE = 24
    GRID_WIDTH = 0.9
    PLT_WIDTH = 9.5
    PLT_HEIGHT = 5.5
    PLOT_FACTOR = 0.7
    COLORMAP = 'Blues'
    LABEL_COLOR = 'grey'
    GRID_COLOR = 'white'
    CHINESE_RE = '[\u4e00-\u9fff]+'
    MIN_VALUE_COLOR = "aliceblue"
    MAX_VALUE_COLOR = "dodgerblue"
    XTICKS_ROTATION = 90


class TaggedCityMapStyle:
    MARKER_SIZE = 17
    MARKER_OPACITY = 0.3
    MARKER_COLOR = 'dodgerblue'
    ZOOM = 12
    MARGIN = dict(l=0, r=30, b=0, t=20)
    MAP_WIDTH = 800
    MAP_HEIGHT = 470
    MAX_MARKER_SIZE = 40
    MIN_MARKER_SIZE = 3
    FONT_SIZE = 12
    FONT_COLOR = 'royalblue'
    MIN_LOCATIONS = 6


class LocationsScatterStyle:
    MARKER_OPACITY = 0.5
    MARKER_SIZE = 7
    PLOT_HEIGHT = 450
    PLOT_WIDTH = 600
    TARGET_COLOR = 'orangered'
    OPPOSITE_COLOR = 'gold'
    ANNOTATION_BACKGROUND = 'orangered'
    ANNOTATION_FONT_SIZE = 14
    ANNOTATION_OPACITY = 0.95
    ANNOTATION_FONT_COLOR = 'white'
    ANNOTATION_FONT_NAME = 'arial'
    MARGIN = dict(l=0, r=30, b=0, t=20)
