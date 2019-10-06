$(function () {
    "use strict";

    /*----------------------------------------------------*/
// Select2
    /*----------------------------------------------------*/
    $('.select2').select2({
        minimumResultsForSearch: Infinity,
    });


    /*----------------------------------------------------*/
// Search.
    /*----------------------------------------------------*/
    $(document).on('click', '.search-open', function (event) {
        $('body').addClass('search-opened');
        event.preventDefault();
    });

    $(document).on('click', '.search-close', function (event) {
        $('body').removeClass('search-opened');
        event.preventDefault();
    });

    /*----------------------------------------------------*/
// Superfish menu.
    /*----------------------------------------------------*/
    $('.sf-menu').superfish();

    /*----------------------------------------------------*/
// Superslides
    /*----------------------------------------------------*/
    var height = $(window).height();
    $('#home-inner').height(height);

    $('#slides').superslides({
        play: 7000,
        animation: 'slide', // slide
        pagination: false,
        inherit_height_from: '#home-inner',
    });

    /*----------------------------------------------------*/
// Fancybox
    /*----------------------------------------------------*/
    $("a.popup-link").fancybox();


    /*----------------------------------------------------*/
// sticky header
    /*----------------------------------------------------*/
    /*
for fixed header onScroll().
*/
// When the user scrolls the page, execute myFunction 
window.onscroll = function() {myFunction()};

// Get the header
var header = document.querySelector(".top2-wrapper");

// Get the offset position of the navbar
var sticky = header.offsetTop;

// Add the sticky class to the header when you reach its scroll position. Remove "sticky" when you leave the scroll position
function myFunction() {
  if (window.pageYOffset >= sticky) {
    header.classList.add("sticky");
  } else {
    header.classList.remove("sticky");
  }
}


    /*----------------------------------------------------*/
// Datapicker
    /*----------------------------------------------------*/
    $(".datepicker").datepicker({
        orientation: "top"
    });

    /*----------------------------------------------------*/
// owlCarousel
    /*----------------------------------------------------*/
    $('.owl-carousel-wide').owlCarousel({
        items: 1,
        loop: true,
        margin: 50,
        autoplay: true,
        autoplayTimeout: 8000
    });

    $('.owl-carousel-testimonials').owlCarousel({
        center: true,
        items: 1,
        loop: true,
        margin: 30,
        responsive: {
            800: {
                items: 3
            }
        }
    });

    /*----------------------------------------------------*/
// slick
    /*----------------------------------------------------*/
// About.
    $('.slider-for').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false,
        fade: true,
        asNavFor: '.slider-nav',
        adaptiveHeight: true,
        autoplay: true,
        autoplaySpeed: 5000
    });

    $('.slider-nav').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false,
        asNavFor: '.slider-for',
        dots: false,
        centerMode: false,
        focusOnSelect: false,
        adaptiveHeight: true,
        fade: true,
        autoplay: true,
        autoplaySpeed: 5000
    });


    /*----------------------------------------------------*/
// Round animation.
    /*----------------------------------------------------*/
    $('.yjsg-round-progress').appear(function () {
        var elem = $(this);
        var animationDelay = elem.data('animation-delay');
        if (animationDelay) {
            setTimeout(function () {
                $(elem).yjsgroundprogress();
            }, animationDelay);
        } else {
            $(elem).yjsgroundprogress();
        }
    });

    /*----------------------------------------------------*/
// Tabs.
    /*----------------------------------------------------*/
    $(document).on('click', '.tabs a', function (e) {
        e.preventDefault();
        var $this = $(this),
            tabgroup = '#' + $this.parents('.tabs').data('tabgroup'),
            others = $this.closest('li').siblings(),
            target = $this.attr('href');

        others.removeClass('active');
        $this.closest('li').addClass('active');
        $(tabgroup).children('div').hide();
        $(target).show();
    });
    $('.tabs .active a').trigger('click');


    /*----------------------------------------------------*/
// MENU SMOOTH SCROLLING
    /*----------------------------------------------------*/
    $(document).on('click', ".front .navbar_ .navbar-nav a", function (event) {

        //$(".navbar_ .nav a a").removeClass('active');
        //$(this).addClass('active');
        // var headerH = $('#top1').outerHeight();
        var headerH = $('#top-inner').outerHeight();

        if ($(this).attr("href") == "#home") {
            $("html, body").animate({
                scrollTop: 0 + 'px'
                // scrollTop: $($(this).attr("href")).offset().top + 'px'
            }, {
                duration: 1200,
                easing: "easeInOutExpo"
            });
        }
        else {
            $("html, body").animate({
                scrollTop: $($(this).attr("href")).offset().top - headerH + 'px'
                // scrollTop: $($(this).attr("href")).offset().top + 'px'
            }, {
                duration: 1200,
                easing: "easeInOutExpo"
            });
        }

        $(this).blur();


        event.preventDefault();
    });



    // Details.
    $('.slider-for2').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false,
        fade: true,
        asNavFor: '.slider-nav2',
        adaptiveHeight: true,
        autoplay: true,
        autoplaySpeed: 5000
    });

    $('.slider-nav2').slick({
        // slidesToShow: 5,
        slidesToScroll: 1,
        arrows: false,
        asNavFor: '.slider-for2',
        dots: false,
        centerMode: false,
        focusOnSelect: true,
        adaptiveHeight: false,
        fade: false,
        autoplay: true,
        autoplaySpeed: 5000,
        vertical: true,
        verticalSwiping: true,
        responsive: [
            {
                breakpoint: 767,
                settings: {
                    vertical: false,
                    slidesToShow: 4,
                    slidesToScroll: 1
                }
            },
            {
                breakpoint: 575,
                settings: {
                    vertical: false,
                    slidesToShow: 3,
                    slidesToScroll: 1
                }
            },
            {
                breakpoint: 480,
                settings: {
                    vertical: false,
                    slidesToShow: 2,
                    slidesToScroll: 1
                }
            }
        ]
    });
});
