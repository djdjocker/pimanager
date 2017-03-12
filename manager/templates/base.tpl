<html>
<head>
    <title />
    <css />
</head>
<body class="show-modal-transparent">
    <div id="plex" class="application show-nav-bar">
        <div class="nav-bar">
            <ul class="nav nav-bar-nav">
                <li><a class="back-btn hidden" href="#"><i class="glyphicon chevron-left" />&nbsp;</a></li>
                <li><a class="home-btn hidden" href="#"><i class="glyphicon home" /></a>&nbsp;</li>
            </ul>
            
            <ul class="nav nav-bar-nav nav-bar-right">
                <li><a class="settings-btn" href="/settings" title="" data-toggle="tooltip" data-original-title="Réglages"><i class="glyphicon settings" />&nbsp;</a></li>
                <li><a class="gui-btn" href="/gui" ><i class="plex-icon-companion-cast" />&nbsp;</a></li>
            </ul>
        </div>
        <div class="background-container">
            <div data-reactroot="">
                <div>
                    <div>
                        <div class="" style="background-image: url(&quot;/static/src/img/preset-dark.png&quot;); background-size: cover; background-position: center center; width: 100%; height: 100%; position: absolute; z-index: 2;"></div>
                    </div>
                    <div style="position: absolute; width: 100%; height: 100%; background: url(&quot;/static/src/img/noise.png&quot;); z-index: 2;"></div>
                </div>
                <!-- react-empty: 6 -->
            </div>
        </div>
        <div id="content" class="scroll-container dark-scrollbar" >
             <content />
        </div>
    </div>
    <js />
</body>
</html>