$(function () {
    var $overscan = $('#modal-setting-overscan');
    var stage = -1;
    var shown = false;
    var synced = $.cookie("synced");
    
    function poll(deffered){
       setTimeout(function(){
          $.ajax({ url: "/gui/longpoll/setting-overscan", success: function(response){
            if (synced == 'localhost'){
                if (response == -1 && shown) {
                    $overscan.modal('hide');
                } else if (response != -1 && !shown){
                    $overscan.modal('show');
                } else if (response != stage) {
                    set_stage(reponse);
                }
                poll(deffered);
            } else if (synced == "remote"){
                if (stage != remote){
                    poll(deffered);
                } else if (deffered) {
                    deffered.resolve();
                }
            }
          }, dataType: "json"});
      }, 30000);
    };
    
    function set_stage(s){
        stage = s;
        $overscan.find('[data-overscan-state]').hide();
        
        $overscan.unbind('keydown');
        
        $.post({ 
            url: "/gui/longpoll/set-setting-overscan-stage", 
            data:stage, 
            success: function(response){
                if (stage == -1) {
                    $overscan.modal('hide');
                } else if (synced == 'localhost' && stage == 0){
                    set_stage(1);
                    bind_events();
                    $overscan.find('[data-overscan-state="'+s+'"]').show();
                } else if (synced == 'remote') {
                    $overscan.find('[data-overscan-state="0"]').show();
                    var deffered = $.Deffered();
                    
                    deffered.done(function (){
                        bind_events();
                        $overscan.find('[data-overscan-state="'+s+'"]').show();
                    });
                    
                    poll(deffered);
                }
            }
        });
    };
    
    function bind_events(){
        $overscan.focus();
        $overscan.bind('keydown', function(event) {
            switch(event.keyCode){
               case 13:
                    $(this).modal('hide');
            }
        });
    };
    
    if (synced == 'localhost'){
        poll();
    }
    
    $overscan.on('hidden.bs.modal', function () {
        //$overscan.unbind('keydown');
        set_stage(-1);
        shown = false;
    });
    
    $overscan.on('show.bs.modal', function () {
        set_stage(0);
        shown = true;
    });
});