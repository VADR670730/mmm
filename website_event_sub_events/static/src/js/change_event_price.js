odoo.define('website_event_sub_events.change_event_price', function (require) {
'use strict';

    var ajax = require('web.ajax');
    var website_event = require('website_event.website_event')

    website_event.EventRegistrationForm.include({
        on_click: function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $form = $(ev.currentTarget).closest('form');
            var $button = $(ev.currentTarget).closest('[type="submit"]');
            var post = {};
            // Get number of tickets ordered for each one
            $("#registration_form select").each(function() {
                post[$(this).attr('name')] = $(this).val();
            });
            // Get all data from all input and give them to the controller
            $("#registration_form input").each(function() {
                post[$(this).attr('name')] = $(this).val();
            });
            return ajax.jsonRpc($form.attr('action'), 'call', post).then(function (modal) {
            // Only needed for 9.0 up to saas-14
            if (modal === false) {
                $button.prop('disabled', false);
                return;
            }
            var $modal = $(modal);
            $modal.modal({backdrop: 'static', keyboard: false});
            $modal.find('.modal-body > div').removeClass('container'); // retrocompatibility - REMOVE ME in master / saas-19
            $modal.insertAfter($form).modal();

            $('.event_role').on('change', function() {
                var roleId = $(this).val();
                var roleCounter = $(this).attr('data-cntr');
                $(".subevents."+roleCounter+"-subevents").find('option').each(function(){
                    var roles = $(this).attr('data-sub-event-roles');
                    if(roles != undefined && roles !=''){
                        var roles_array = roles 
                        if(roles_array.length > 0){
                            if(roles_array.indexOf(roleId) < 0 || roleId == ''){
                                $(this).attr("disabled", true);
                                $(".subevents."+roleCounter+"-subevents option:selected").removeAttr("selected");
                                $(".subevents."+roleCounter+"-subevents").multiselect("refresh");
                            } else {
                                $(this).attr("disabled", false);
                                $(".subevents."+roleCounter+"-subevents option:selected").removeAttr("selected");
                                $(".subevents."+roleCounter+"-subevents").multiselect("refresh");
                            }    
                        } else {
                            $(this).attr("disabled", false);
                            $(".subevents."+roleCounter+"-subevents option:selected").removeAttr("selected");
                            $(".subevents."+roleCounter+"-subevents").multiselect("refresh");
                        }    
                    } else {
                        $(this).attr("disabled", false);
                        $(".subevents."+roleCounter+"-subevents option:selected").removeAttr("selected");
                        $(".subevents."+roleCounter+"-subevents").multiselect("refresh"); 
                    }

                    if($(".subevents."+roleCounter+"-subevents").find('option').length == $(".subevents."+roleCounter+"-subevents").find('option:disabled').length){
                        $("#"+roleCounter+"-select_product").css("display", "none");
                    } else {
                        $("#"+roleCounter+"-select_product").css("display", "block");
                    }

                    /* Set the price without discount */
                    var price_id = $("#"+roleCounter+"-sub_events_multiple_total_price")
                    $("#"+roleCounter+"-sub_events_multiple_total_price").val($(price_id).val());

                    /* Set the price with discount, the one that is showed to the user */
                    var price_discounted_id = $("#"+roleCounter+"-sub_events_multiple_total_price_discounted")
                    $("#"+roleCounter+"-sub_events_multiple_total_price").val($(price_id).val());

                });
            });

            $('.subevents').on('change', function() {
                var sub_ticket_value = parseFloat($(this).attr('data-ticket-price')) || 0.0;
                $(this).find('option:selected').each(function(){
                    sub_ticket_value += parseFloat($(this).attr('data-sub-event-ticket-price')) || 0.0;
                });
                /* Set the price without discount */
                var price_id = "#"+$(this).attr('id')+"_total_price";
                $(price_id).val(sub_ticket_value);

                /* Set the price with discount, the one that is showed to the user */
                var price_discounted_id = "#"+$(this).attr('id')+"_total_price_discounted";
                $(price_discounted_id).val(sub_ticket_value);
            });
            $modal.on('click', '.js_goto_event', function () {
                $modal.modal('hide');
                $button.prop('disabled', false);
            });
            $modal.on('click', '.close', function () {
                $button.prop('disabled', false);
            });
        });
    },
    })
});
