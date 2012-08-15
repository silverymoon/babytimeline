$(function() {
    $('.date').datepicker({ showOn: "button",
                            buttonImage: '/site_media/images/calendar.gif',
                            buttonImageOnly : true,
                            showButtonPanel : true,
                            dateFormat: 'yy-mm-dd'});
    $('.date').datepicker('option', $.datepicker.regional['de']);
});
