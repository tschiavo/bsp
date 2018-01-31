function gen(tmpl_url, data_url, dest_sel) {
	$.get(tmpl_url, function(tmpl_data,tmpl_status) {
		$.get(data_url, function(data_data,data_status) {
			var tempFn = doT.template(tmpl_data);
			var o = $.parseJSON(data_data);
			var resultText = tempFn(o);
			$(dest_sel).append(resultText);
		});
	});
};

function gen_moods() {
	gen('mood_tmpl.doT', 'moods', '#maincontent');
}

function clear_main() {
	$('#maincontent').empty();
}

window.onload=function() {
	//if(window.location.pathname == '/messages') {
	//	clear_main();
	//	gen_moods();
	//}
    
    $('#notification').hide();

    //timeouttime = 10000;
    retrycooldown = 1000;

    startpoll = function(successfunc) {
        $.ajax({ 
            url: 'data_stream', 
            success: successfunc, 
            error: function(x,t,m) { 
                setTimeout(
                    function() { startpoll(successfunc); }, 
                    retrycooldown 
                )
            }
        });
    }

    successfunc = function(txt) {
        if(txt.indexOf('refresh the page homie') != -1) {
            $('#notification').show();
            if(document.title.indexOf('(!)') == -1)
            {
                document.title = '(!) ' + document.title;
            }
        }
        startpoll(successfunc);
    }

    // Need a timeout on starting polls so that onLoad can return
    // control back to cordova since it appears to be doing
    // onLoad on the main UI thread.
    
    // Turning off the long poll
    // setTimeout(function() { startpoll(successfunc); }, 10);
}


