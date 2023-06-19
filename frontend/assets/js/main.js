
(function() {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    let selectEl = select(el, all)
    if (selectEl) {
      if (all) {
        selectEl.forEach(e => e.addEventListener(type, listener))
      } else {
        selectEl.addEventListener(type, listener)
      }
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener)
  }

  /**
   * Toggle .header-scrolled class to #header when page is scrolled
   */
  let selectHeader = select('#header')
  if (selectHeader) {
    const headerScrolled = () => {
      if (window.scrollY > 100) {
        selectHeader.classList.add('header-scrolled')
      } else {
        selectHeader.classList.remove('header-scrolled')
      }
    }
    window.addEventListener('load', headerScrolled)
    onscroll(document, headerScrolled)
  }

  /**
   * Mobile nav toggle
   */
  on('click', '.mobile-nav-toggle', function(e) {
    select('#navbar').classList.toggle('navbar-mobile')
    this.classList.toggle('bi-list')
    this.classList.toggle('bi-x')
  })

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }

  /**
   * Mobile nav dropdowns activate
   */
  on('click', '.navbar .dropdown > a', function(e) {
    if (select('#navbar').classList.contains('navbar-mobile')) {
      e.preventDefault()
      this.nextElementSibling.classList.toggle('dropdown-active')
    }
  }, true)

  /**
   * Testimonials slider
   */
  new Swiper('.testimonials-slider', {
    speed: 600,
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false
    },
    slidesPerView: 'auto',
    pagination: {
      el: '.swiper-pagination',
      type: 'bullets',
      clickable: true
    }
  });

  /**
   * Animation on scroll
   */
  window.addEventListener('load', () => {
    AOS.init({
      duration: 1000,
      easing: 'ease-in-out',
      once: true,
      mirror: false
    })
  });

})()


function preview() {

  var parent = document.getElementById('preview-row');
  var frame_source = document.getElementById("frame_source");

  if (frame_source != null) {
      parent.removeChild(frame_source);
  }

  var frame_source_url= document.getElementById("frame_source_url");
  if (frame_source_url != null) {
      parent.removeChild(frame_source_url);
  }

  var frame_source = document.createElement("img");
  frame_source.id = "frame_source";
  frame_source.className = "img-fluid mx-auto d-block";
  frame_source.setAttribute("data-aos", "fade-right");
  frame_source.style.marginTop = "5%";
  frame_source.style.marginBottom = "5%";
  // frame_source.style.float = "none";
  frame_source.src = URL.createObjectURL(document.getElementById("formFile_src").files[0]);
  parent.append(frame_source);

}


document.addEventListener('DOMContentLoaded', function () {

  if (document.getElementById("formFile_src").files.length != 0) {
      preview();
  }

});


switcher = document.getElementById('view-switch')
switcher.onclick = function () {
  $('#img-upload').toggle(500);
  $('#showtime-row').toggle(500);
  $('#showtimeUrl-row').toggle(500);
  $('#img-url').toggle(500)
  $('#options-row').toggle(250).toggle(250)
}


async function testImages(click) {
  photo_src_url = document.getElementById("source-url").value;

  src_valid = undefined;

  $('#frame_source_url').hide();
  $('#loader_src').show();

  const srcTask = testImage(photo_src_url).then(
      function () { 
          src_valid = true;
          previewUrl();
   }, function () { 
          src_valid = false;
          $('#frame_source_url').hide(500, function() {$(this).remove()});
       });

  await srcTask
  
  $('#loader_src').hide();

  if(click){
      sendUrl(src_valid);
  }
}


function testImage(url) {
  return new Promise(function (resolve, reject) {
      var timeout = 1500;
      var timer, img = new Image();
      img.onerror = img.onabort = function () {
          clearTimeout(timer);
          reject("error");
      };
      img.onload = function () {
          clearTimeout(timer);
          resolve("success");
      };
      timer = setTimeout(function () {
          // reset .src to invalid URL so it stops previous
          // loading, but doens't trigger new load
          img.src = "//!!!!/noexist.jpg";
          reject("timeout");
      }, timeout);
      img.src = url;
  });
}


function previewUrl() {

  parent = document.getElementById('preview-row');
  frame_source = document.getElementById("frame_source_url");

  if (frame_source != null) {
      parent.removeChild(frame_source);
  }

  frame_source_file = document.getElementById("frame_source");
  if (frame_source_file != null) {
    parent.removeChild(frame_source_file);
  }

  frame_source = document.createElement("img");
  frame_source.id = "frame_source_url";
  frame_source.className = "img-fluid mx-auto d-block";
  frame_source.setAttribute("data-aos", "fade-right");
  frame_source.style.marginTop = "5%";
  frame_source.style.marginBottom = "5%";
  frame_source.src = document.getElementById("source-url").value;
  parent.append(frame_source);

}