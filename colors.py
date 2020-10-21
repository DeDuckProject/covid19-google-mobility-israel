import matplotlib._color_data as mcd

cssColors = mcd.CSS4_COLORS
xkcdColors = list(mcd.XKCD_COLORS.values())
# colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', cssColors['royalblue'], '#a569bd', cssColors['mediumslateblue'], cssColors['salmon'], cssColors['limegreen'], cssColors['hotpink'], cssColors['cadetblue'], cssColors['darkorange'], cssColors['rebeccapurple'], cssColors['firebrick'], cssColors['teal'], cssColors['blueviolet']] # original matplotlib colors with some addition
colors = [cssColors['mediumblue'], cssColors['orange'], cssColors['limegreen'], cssColors['tomato'], cssColors['blueviolet'], cssColors['sienna'], cssColors['hotpink'], cssColors['slategray'], '#bcbd22', cssColors['dodgerblue'], cssColors['mediumslateblue'], cssColors['darkseagreen'], cssColors['salmon'], cssColors['pink'], cssColors['lightcoral'], cssColors['cadetblue'], cssColors['rebeccapurple'], cssColors['teal']] # prettier colors + addition
def getColorByIndex(n):
    if n>=len(colors):
        return xkcdColors[n]
    else:
        return colors[n]