<div class="container">
    <ul class="nav nav-header pull-right">
        <li class="web-nav-item">
            <a class="web-btn btn-gray selected" href="/config/general">Général</a>
        </li>
        
        <li class="server-nav-item hidden">
            <a class="server-btn btn-gray " href="/settings/plex">Plex</a>
        </li>
    </ul>

    <h2>Réglages</h2>

    <div class="settings-container">
        <div class="general-settings-container">
            <div class="row">
                <div class="col-sm-4 col-md-3">
                    <ul class="settings-nav nav nav-cards">
                        <li><a class="card btn-gray selected" href="#general-affichage-group">Affichage</a></li>
                        <li><a class="card btn-gray" href="#general-modules-group">Modles</a></li>
                    </ul>
                </div>

                <div class="col-sm-8 col-md-9"> 
                    <form id="general-config-form">
                        <div id="general-web-group" class="settings-group active">
                            <div class="form-group">
                                <label for="language">Overscreen</label>
                                <label class="switch">
                                  <input type="checkbox">
                                  <div class="slider round"></div>
                                </label>
                                <p class="help-block">Activez l'overscreen pour régler les marges autour de l'écran.</p>
                            </div>

                            <!--div class="form-group">
                                <label class="control-label"><input type="checkbox" id="autoLogin"> Connexion automatique </label>
                                <p class="help-block">Ne pas demander de sélectionner un utilisateur ou de saisir un code PIN lors du lancement sur cet appareil.</p>
                            </div>

                            <div class="form-group"> 
                                <label class="control-label"> <input type="checkbox" id="playThemeMusic"> Jouer les thèmes musicaux </label>
                                <p class="help-block">Joue automatiquement les fonds musicaux quand disponibles (par ex. le générique d'une série quand vous explorez celle-ci).</p>
                            </div>

                            <div class="form-group">
                                <label class="control-label"> <input type="checkbox" id="keyboardShortcuts" checked=""> Activer les raccourcis clavier </label>
                                <p class="help-block">Appuyer sur ? pour afficher la liste des <a class="keyboard-shortcuts-btn" href="#">raccourcis clavier disponibles</a>.</p>
                            </div>

                            <div class="form-group">
                                <label class="control-label"> <input type="checkbox" id="companion" checked=""> Publier en tant que Lecteur </label>
                                <p class="help-block">Allow other Plex apps to fling content to this device and control it remotely.</p>
                            </div>

                            <div class="form-group">
                                <label for="allowHttpFallback">Autoriser le retour aux connexions non sécurisées</label>
                                <select id="allowHttpFallback">
                                    <option value="never" selected="">Never</option>
                                    <option value="samenetwork">On same network as server</option>
                                    <option value="always">Always</option>
                                </select>
                                <p class="help-block">Autoriser ce navigateur à effectuer des connexions non sécurisées à Plex Media Server si les connexions sécurisées échouent.</p>
                            </div>

                            <div class="form-group">
                                <label for="timeFormat">Format de temps</label>
                                <select id="timeFormat"> 
                                    <option value="h:mma" selected="">12 heures</option>
                                    <option value="HH:mm">24 heures</option>
                                </select>
                            </div-->
                        </div>

                        <div id="general-modules-group" class="settings-group">
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>