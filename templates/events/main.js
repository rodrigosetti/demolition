// Things to do when DOM loaded
$(document).ready(function() {
    $('.hidden_submit').hide();
    $('#user_forms, #event_info').hide();
});

/*
    Ajax form ritual(show loader, hide button, show message) to
    submit user data
*/
function submituser() {

	// validate
	$('#user_data_error').hide();

	first_name = $('input#first_name').val();
	last_name = $('input#last_name').val();
    phone = $('input#phone').val()
	email = $('input#email').val();
	
	if (first_name == '' || last_name == '' ||
        email == '' || phone == '') {
		$('#user_data_error').slideDown();
		return false;
	}

    // send data
	$('#submit_user').hide();
	$('#user_data_loader').show();
	$('#user_data_done').hide();

    var data = {'first_name': first_name,
               'last_name': last_name,
               'email': email, 
			   'phone': phone, 
			   'gender': $('select#gender').val()};

    $.ajax({
      type: "POST",
      url: "{% url registration_save %}",
      data: data,
      success: function() {
      	$('#user_data_loader').hide();
		$('#user_data_done').show();
		$('#user_data_done').fadeOut(4000);

        // update full name show
        $('#full_name').html(first_name + ' ' + last_name);
      }
    });

    return false;
};

/*
    Ajax form ritual(show loader, hide button, show message) to
    change password.
*/
function submitpassword() {

	// validate
	$('#password_error').hide();
	
	passwd = $('input#password1').val();
	passwdc = $('input#password2').val();
	
	if (passwd == '' || passwd != passwdc) {
		$('#password_error').slideDown();
		return false;
	}
	
	// send data
	$('#submit_password').hide();
	$('#password_change_loader').show();
	$('#password_done').hide();

    var data = {'password1': passwd,
			    'password2': passwdc};

    $.ajax({
      type: "POST",
      url: "{% url registration_password %}",
      data: data,
      success: function() {
        $('#password_change_loader').hide();
		$('#password_done').show();
		$('#password_done').fadeOut(4000);
      }
    });

	// clear
	$('input#password1').val('');
	$('input#password2').val('');

    return false;
};

/*
    Ajax form ritual(show loader, hide button, show message) to
    save participation preferences
*/
function participationprefs(post_url) {

    // show loader and hide submit(ajax form)
	$('#prefs_loader').show();
	$('#submit_prefs').hide();
    $('#charge').html('<img src="{{ MEDIA_URL }}image/loader.gif">');

    // build data	
    data = {};
    if ($('#drinking').is(':checked'))
        data['drinking'] = 'on';
    if ($('#self_transportation').is(':checked'))
        data['self_transportation'] = 'on';
    if ($('#offer_ride').is(':checked'))
        data['offer_ride'] = 'on';

	// send data
	$.ajax({
            type: "POST",
            url: post_url,
            data: data,
			dataType: 'json',
            success: function(data) {
                $('#prefs_loader').hide();
                $('#prefs_done').show();
                $('#prefs_done').fadeOut(4000);

                // update charge
				$('#charge').html(data["charge"]);
            }
        });

    return false;
};

/*
    Ajax form ritual(show loader, hide button, show message) to
    save participation dates
*/
function savedates(post_url) {
    // compose data dinamicaly from date_<id> objects
    data = {};
    $('#dates li input:checked').each(function(idx, item) {
        data[item.id] = "on";
    });

	// show and hide dynamic form
	$('#dates_loader').show();
	$('#submit_dates').hide();
    $('#charge').html('<img src="{{ MEDIA_URL }}image/loader.gif">');

    // send data
	$.ajax({
            type: "POST",
            url: post_url,
            data: data,
			dataType: 'json',
            success: function(data) {
                $('#dates_loader').hide();
                $('#dates_done').show();
                $('#dates_done').fadeOut(4000);

                // update charge
				$('#charge').html(data["charge"]);
            }
        });

    return false;
}

/*
    When a user request a invitation from a event page which he
    does not have a participation object this function is called.
    It does the Ajax form ritual(show loader, hide button, show message)
    and sends an Ajax POST request to the proper url in order to create
    the Participation object related.
*/
function requestinvitation(post_url) {

	// show and hide dynamic form
	$('#invitation_loader').show();
	$('#submit_invitation_req').hide();
	
    // send data
	$.ajax({
          type: "POST",
          url: post_url,
          success: function() {
            $('#invitation_loader').hide();
			$('#invitation_done').fadeIn();
          }
        });

    return false;
};

/*
    Tab behavior: when a event link is clicked this function is called
    in order to show the "loader" gif and load the proper participation
    details HTML into the #participation container.
*/
function loadparticipation(post_url) {

    $('#participation').html('<img src="{{ MEDIA_URL }}image/loader.gif">');
    $('#participation').load(post_url, function() {
        $('#participation .hidden_submit, #event_info').hide();
    });

    return false;
};

/*
    Simple toggler to show and hide user edition division
*/
var editing_user = false;
function toggleuseredit() {

    if (editing_user) {
        $('#user_forms').slideUp();
        $('#collapse_edit').attr('src', '{{ MEDIA_URL }}image/plus.gif');
    }
    else {
        $('#user_forms').slideDown();
        $('#collapse_edit').attr('src', '{{ MEDIA_URL }}image/minus.gif');
    }

    editing_user = !editing_user;
};

/*
    Simple toggler to show and hide event info
*/
var show_event_info = false;
function toggleeventinfo() {

    if (show_event_info) {
        $('#event_info').slideUp();
        $('#collapse_event_info').attr('src', '{{ MEDIA_URL }}image/plus.gif');
    }
    else {
        $('#event_info').slideDown();
        $('#collapse_event_info').attr('src', '{{ MEDIA_URL }}image/minus.gif');
    }

    show_event_info = !show_event_info;
};

/*
    Adds a new li item with a conpanion form into ul#companions list
*/
function addcompanion(post_url) {

    // show loader
    $('#addcompanion_loader').show();
    $('#charge').html('<img src="{{ MEDIA_URL }}image/loader.gif">');

    // make call to url in order to obtain html
    $.post(post_url, {}, function(data) {
        // append li element html into list
        $('ul#companions').append(data["html"]);
        $('ul#companions li:last-child').hide();
        $('ul#companions li:last-child').slideDown();
        $('ul#companions li:last-child .hidden_submit').hide();

        // update charge
		$('#charge').html(data["charge"]);

        // hide loader
        $('#addcompanion_loader').hide();
      }, "json");

    return false;
};

/*
    Deletes companion item calling Ajax method and removing from list
*/
function deletecompanion(post_url, id) {

    // show loader
    $('#addcompanion_loader').show();
    $('#charge').html('<img src="{{ MEDIA_URL }}image/loader.gif">');

    // send request
    $.ajax({
      type: "POST",
      data: {"id": id},
      url: post_url,
	  dataType: 'json',
      success: function(data) {            
        // slide up element(hide)
        $('#companion_' + id).slideUp('slow', function() {
            // remove element
            $('#companion_' + id).remove();

            // update charge
			$('#charge').html(data["charge"]);

            // hide loader
            $('#addcompanion_loader').hide();
        });
      }
    });

    return false;
};

/*
    Edit companion item calling Ajax form
*/
function savecompanion(post_url, id) {

    // gather data
    data = { 'id' : id,
            'gender': $('#companion_form_' + id + ' select[name=gender]').val()};

    if ( $('#companion_form_' + id + ' input[name=drinking]').is(':checked') )
        data['drinking'] = 'on';

    // show and hide dynamic form
	$('#companion_loader_' + id).show();
	$('#submit_companion_' + id).hide();
    $('#charge').html('<img src="{{ MEDIA_URL }}image/loader.gif">');
	
    // send data
	$.post(post_url, data, function(data) {
            $('#companion_loader_' + id).hide();
            $('#companion_done_' + id).show()
			$('#companion_done_' + id).fadeOut(4000);

            // update charge
			$('#charge').html(data["charge"]);
          }, 'json');

    return false;
};

/*
    Updates comments
*/
function updatecomments(url) {

	$('#comments_loader').show();
	$('#comments_update').hide();

    // send request
    $.get(url, {}, function(data) {
        $('ul#comment_list').html(data);
	    $('#comments_loader').hide();
	    $('#comments_update').show();
    }, 'html');

    return false;
};

/*
    Insert comment
*/
function postcomment(add_url, update_url) {

    data = {'comment_text': $('#comment_text').val()};

    // send request
    $.post(add_url, data, function() {
        // update comments
        updatecomments(update_url);

        // removes text from area
        $('#comment_text').attr('value', '');
    });

    return false;
};

/*
    Removes comment
*/
function removecomment(remove_url, update_url, id) {

    // send request
    $.post(remove_url, {'id': id}, function() {
        // update comments
        updatecomments(update_url);
    });

    return false;
};
