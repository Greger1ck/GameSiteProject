

(function () {
  function qsAll(root, sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); }

  function Gallery(viewport) {
    this.viewport = viewport;
    this.slides = qsAll(viewport, '.gallery__slide');
    this.prevBtn = viewport.querySelector('.gallery__ctrl--prev');
    this.nextBtn = viewport.querySelector('.gallery__ctrl--next');


    this.thumbsWrap = viewport.parentElement.querySelector('.thumbs');
    this.thumbs = this.thumbsWrap ? qsAll(this.thumbsWrap, '.thumb') : [];

    this.index = 0;
    this.interval = parseInt(viewport.getAttribute('data-interval') || '0', 10);
    this.timer = null;

    this.bind();
    this.goto(0, false);
    this.autoplay(true);
  }

  Gallery.prototype.bind = function () {
    var self = this;

    if (this.prevBtn) {
      this.prevBtn.addEventListener('click', function (e) {
        e.preventDefault(); e.stopPropagation();
        self.prev();
      });
    }

    if (this.nextBtn) {
      this.nextBtn.addEventListener('click', function (e) {
        e.preventDefault(); e.stopPropagation();
        self.next();
      });
    }

    if (this.thumbs.length) {
      this.thumbs.forEach(function (btn, i) {
        btn.addEventListener('click', function () {
          self.goto(i);
        });
      });
    }


    this.viewport.addEventListener('mouseenter', this.autoplay.bind(this, false));
    this.viewport.addEventListener('mouseleave', this.autoplay.bind(this, true));


    var startX = null;
    this.viewport.addEventListener('touchstart', function (e) {
      startX = e.touches[0].clientX;
    }, {passive:true});
    this.viewport.addEventListener('touchend', function (e) {
      if (startX == null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 30) { dx > 0 ? self.prev() : self.next(); }
      startX = null;
    });
  };

  Gallery.prototype.autoplay = function (on) {
    var self = this;
    if (!this.interval || this.interval < 400) { 
      if (this.timer) clearInterval(this.timer);
      this.timer = null;
      return;
    }
    if (on) {
      if (this.timer) return;
      this.timer = setInterval(function () { self.next(); }, this.interval);
    } else {
      if (this.timer) { clearInterval(this.timer); this.timer = null; }
    }
  };

  Gallery.prototype.updateThumbs = function () {
    if (!this.thumbs.length) return;
    this.thumbs.forEach(function (t) { t.classList.remove('is-active'); });
    var active = this.thumbs[this.index];
    if (active) active.classList.add('is-active');


    if (this.thumbsWrap && active) {
      var wrap = this.thumbsWrap;
      var rect = active.getBoundingClientRect();
      var wrect = wrap.getBoundingClientRect();
      if (rect.right > wrect.right) wrap.scrollLeft += (rect.right - wrect.right) + 12;
      if (rect.left < wrect.left) wrap.scrollLeft -= (wrect.left - rect.left) + 12;
    }
  };

  Gallery.prototype.goto = function (i, animate) {
    if (i < 0) i = this.slides.length - 1;
    if (i >= this.slides.length) i = 0;
    this.index = i;

    for (var s = 0; s < this.slides.length; s++) {
      var el = this.slides[s];
      if (s === i) el.classList.add('is-active');
      else el.classList.remove('is-active');
    }
    this.updateThumbs();
  };

  Gallery.prototype.next = function () { this.goto(this.index + 1, true); };
  Gallery.prototype.prev = function () { this.goto(this.index - 1, true); };


  document.addEventListener('DOMContentLoaded', function () {
    qsAll(document, '.js-auto-gallery').forEach(function (vp) { new Gallery(vp); });


    if (window.jQuery && jQuery.fancybox) {
      jQuery('[data-fancybox="post-gallery"]').fancybox({
        buttons: ['zoom','slideShow','fullScreen','thumbs','close'],
        loop: true,
        animationEffect: "zoom",
      });
    }
  });
})();
