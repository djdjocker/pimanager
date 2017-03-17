<html>
<head>
    <title />
    <css />
</head>
<body class="show-modal-transparent">
    <div id="plex" class="application show-navbar">
        <div class="navbar">
            <ul class="nav navbar-nav">
                <li><a class="back-btn hidden" href="#"><i class="glyphicon chevron-left" />&nbsp;</a></li>
                <li><a class="home-btn hidden" href="#"><i class="glyphicon home" /></a>&nbsp;</li>
            </ul>
            
            <ul class="nav navbar-nav navbar-right">
                <li><a t-if="request.localhost or request.remote" t-att-class="'settings-btn' + (request.path.startswith('/config') and ' active')" href="/config" title="" data-toggle="tooltip" data-original-title="Réglages"><i class="glyphicon settings" />&nbsp;</a></li>
                <li><a t-if="not request.gui" class="gui-btn" href="/gui" ><i class="plex-icon-companion-cast" />&nbsp;</a></li>
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
    <div class="hidden" style="color=black; font-size:40px;">
    <i class="plex-icon-artist-560" />
    <i class="plex-icon-clips-560" />
    <i class="plex-icon-movies-560" />
    <i class="plex-icon-music-560" />
    <i class="plex-icon-photos-560" />
    <i class="plex-icon-plex-chevron" />
    <i class="plex-icon-shows-560" />
    <i class="plex-icon-star-dot-560" />
    <i class="plex-icon-star-empty-560" />
    <i class="plex-icon-star-full-560" />
    <i class="plex-icon-timer" />
    <i class="plex-icon-tv-mode-enter-560" />
    <i class="plex-icon-tv-mode-exit-560" />
    <i class="plex-icon-add-560" />
    <i class="plex-icon-add-to-playlist" />
    <i class="plex-icon-alert-560" />
    <i class="plex-icon-alert-round-560" />
    <i class="plex-icon-analyzing-560" />
    <i class="plex-icon-audio" />
    <i class="plex-icon-avatar-crop-max-560" />
    <i class="plex-icon-avatar-crop-min-560" />
    <i class="plex-icon-calendar-560" />
    <i class="plex-icon-camera-560" />
    <i class="plex-icon-channels-560" />
    <i class="plex-icon-close-560" />
    <i class="plex-icon-companion-cast-active" />
    <i class="plex-icon-companion-cast" />
    <i class="plex-icon-dvr-clock-hour-560" />
    <i class="plex-icon-dvr-clock-minutes-560" />
    <i class="plex-icon-dvr-clock-separator-560" />
    <i class="plex-icon-dvr-series-560" />
    <i class="plex-icon-dvr-single-560" />
    <i class="plex-icon-edit-560" />
    <i class="plex-icon-files-560" />
    <i class="plex-icon-folder-560" />
    <i class="plex-icon-heart-empty" />
    <i class="plex-icon-heart-strikethrough" />
    <i class="plex-icon-heart" />
    <i class="" />
    <i class="plex-icon-hub-next-560" />
    <i class="plex-icon-hub-prev-560" />
    <i class="plex-icon-info-560" />
    <i class="plex-icon-lock-560" />
    <i class="plex-icon-lyrics" />
    <i class="plex-icon-more-560" />
    <i class="plex-icon-osd-repeat-one" />
    <i class="plex-icon-osd-repeat" />
    <i class="plex-icon-osd-shuffle" />
    <i class="plex-icon-page-next-560" />
    <i class="plex-icon-page-prev-560" />
    <i class="plex-icon-personal-cloud-560" />
    <i class="plex-icon-play-560" />
    <i class="plex-icon-play-strip" />
    <i class="plex-icon-player-fullscreen-560" />
    <i class="plex-icon-player-pause-560" />
    <i class="plex-icon-player-video-settings-560" />
    <i class="plex-icon-player-windowed-560" />
    <i class="plex-icon-playlists-560" />
    <i class="plex-icon-pp-badge-560" />
    <i class="plex-icon-recommended-560" />
    <i class="plex-icon-reload-560" />
    <i class="plex-icon-remove-560" />
    <i class="plex-icon-reorder-560" />
    <i class="plex-icon-search-560" />
    <i class="plex-icon-selected-560" />
    <i class="plex-icon-settings-560" />
    <i class="plex-icon-shows-broadcast-560" />
    <i class="plex-icon-sort-ascending-560" />
    <i class="plex-icon-sort-descending-560" />
    <i class="plex-icon-status-560" />
    <i class="plex-icon-subtitles-alt" />
    <i class="plex-icon-tag-auto-560" />
    <i class="plex-icon-tagging-560" />
    <i class="plex-icon-toolbar-add-to-playlist-560" />
    <i class="plex-icon-toolbar-artwork-560" />
    <i class="plex-icon-toolbar-column-560" />
    <i class="plex-icon-toolbar-detail-560" />
    <i class="plex-icon-toolbar-edit-560" />
    <i class="plex-icon-toolbar-filter-add-560" />
    <i class="plex-icon-toolbar-filter-remove-560" />
    <i class="plex-icon-toolbar-grid-560" />
    <i class="plex-icon-toolbar-more-560" />
    <i class="plex-icon-toolbar-play-560" />
    <i class="plex-icon-toolbar-play-trailer-560" />
    <i class="plex-icon-toolbar-shuffle-560" />
    <i class="plex-icon-toolbar-sync-560" />
    <i class="plex-icon-toolbar-watched-toggle-560" />
    <i class="plex-icon-trash-560" />
    <i class="plex-icon-triangle-left" />
    <i class="plex-icon-triangle-right" />
    <i class="plex-icon-unlock-560" />
    <i class="plex-icon-watch-later-560" />
    
    </div>
    
    <extras />
    <js />
</body>
</html>