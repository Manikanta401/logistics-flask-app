(function ($) {
    "use strict";


    /*==================================================================
     [ Validate ]*/
    var input = $('.validate-input .input100');

    $('.validate-form').on('submit', function () {
        var check = true;

        check = validate(input)

        if (check == false)
            showValidate(input)
        console.log(check)
        return check;
    });


    /*$('.validate-form .input100').each(function () {
        $(this).focus(function () {
            hideValidate(this);
        });
    });*/

    function validate(input) {
        if ($(input).attr('type') == 'tel' || $(input).attr('number') == 'tel') {
            if ($(input).val().trim().match(/^\d{10}$/) == null) {
                return false;
            }
        }
        else {
            if ($(input).val().trim() == '') {
                return false;
            } else {
                if ($(input).val().trim().match(/^\d{10}$/) == null) {
                    return false;
                }
            }
        }
    }

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
    }


})(jQuery);