/**
 * Apple-Inspired Micro-Interactions
 * Smooth, responsive, premium feel
 */

(function() {
  'use strict';

  // ========================================
  // Navigation History Fix
  // ========================================
  const NavigationManager = {
    init() {
      // Prevent duplicate history entries
      this.preventDuplicateHistory();
      // Handle back button properly
      this.handleBackButton();
    },

    preventDuplicateHistory() {
      // Replace history after redirects to prevent multi-click back issues
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('redirect') === 'true') {
        history.replaceState(null, '', window.location.pathname);
      }
    },

    handleBackButton() {
      window.addEventListener('popstate', function(event) {
        // Smooth transition on back button
        document.body.style.opacity = '0';
        setTimeout(() => {
          window.location.reload();
        }, 150);
      });
    }
  };

  // ========================================
  // Smooth Page Transitions
  // ========================================
  const PageTransitions = {
    init() {
      this.fadeInOnLoad();
      this.smoothLinkTransitions();
    },

    fadeInOnLoad() {
      document.addEventListener('DOMContentLoaded', () => {
        document.body.classList.add('fade-in');
      });
    },

    smoothLinkTransitions() {
      document.querySelectorAll('a:not([target="_blank"])').forEach(link => {
        link.addEventListener('click', function(e) {
          const href = this.getAttribute('href');
          
          // Skip for anchors, javascript:, and external links
          if (!href || href.startsWith('#') || href.startsWith('javascript:') || 
              href.startsWith('http') && !href.includes(window.location.hostname)) {
            return;
          }

          e.preventDefault();
          document.body.style.opacity = '0.8';
          document.body.style.transition = 'opacity 200ms ease';
          
          setTimeout(() => {
            window.location.href = href;
          }, 200);
        });
      });
    }
  };

  // ========================================
  // Form Enhancements
  // ========================================
  const FormEnhancements = {
    init() {
      this.addFloatingLabels();
      this.addLoadingStates();
      this.addValidationFeedback();
    },

    addFloatingLabels() {
      document.querySelectorAll('.form-control').forEach(input => {
        // Add focus/blur effects
        input.addEventListener('focus', function() {
          this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
          if (!this.value) {
            this.parentElement.classList.remove('focused');
          }
        });

        // Initialize state
        if (input.value) {
          input.parentElement.classList.add('focused');
        }
      });
    },

    addLoadingStates() {
      document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
          const submitBtn = this.querySelector('[type="submit"]');
          if (submitBtn && !submitBtn.disabled) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
              <span class="spinner-border spinner-border-sm me-2"></span>
              Processing...
            `;
          }
        });
      });
    },

    addValidationFeedback() {
      document.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('invalid', function(e) {
          e.preventDefault();
          this.classList.add('is-invalid');
          
          // Add shake animation
          this.style.animation = 'shake 0.3s';
          setTimeout(() => {
            this.style.animation = '';
          }, 300);
        });

        input.addEventListener('input', function() {
          if (this.classList.contains('is-invalid') && this.validity.valid) {
            this.classList.remove('is-invalid');
          }
        });
      });
    }
  };

  // ========================================
  // Card Interactions
  // ========================================
  const CardInteractions = {
    init() {
      this.addHoverEffects();
      this.addClickEffects();
    },

    addHoverEffects() {
      document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
          this.style.transform = 'translateY(-4px)';
        });

        card.addEventListener('mouseleave', function() {
          this.style.transform = 'translateY(0)';
        });
      });
    },

    addClickEffects() {
      document.querySelectorAll('.card[data-href]').forEach(card => {
        card.style.cursor = 'pointer';
        
        card.addEventListener('click', function() {
          const href = this.getAttribute('data-href');
          if (href) {
            window.location.href = href;
          }
        });
      });
    }
  };

  // ========================================
  // Button Interactions
  // ========================================
  const ButtonInteractions = {
    init() {
      this.addRippleEffect();
      this.addHapticFeedback();
    },

    addRippleEffect() {
      document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
          const ripple = document.createElement('span');
          const rect = this.getBoundingClientRect();
          const size = Math.max(rect.width, rect.height);
          const x = e.clientX - rect.left - size / 2;
          const y = e.clientY - rect.top - size / 2;

          ripple.style.width = ripple.style.height = size + 'px';
          ripple.style.left = x + 'px';
          ripple.style.top = y + 'px';
          ripple.classList.add('ripple');

          this.appendChild(ripple);

          setTimeout(() => ripple.remove(), 600);
        });
      });
    },

    addHapticFeedback() {
      // Subtle scale effect on click
      document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('mousedown', function() {
          this.style.transform = 'scale(0.98)';
        });

        button.addEventListener('mouseup', function() {
          this.style.transform = 'scale(1)';
        });
      });
    }
  };

  // ========================================
  // Alert Auto-Dismiss
  // ========================================
  const AlertManager = {
    init() {
      this.autoDismissAlerts();
      this.addCloseButtons();
    },

    autoDismissAlerts() {
      document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
        setTimeout(() => {
          alert.style.opacity = '0';
          alert.style.transform = 'translateY(-20px)';
          setTimeout(() => alert.remove(), 300);
        }, 5000);
      });
    },

    addCloseButtons() {
      document.querySelectorAll('.alert').forEach(alert => {
        if (!alert.querySelector('.alert-close')) {
          const closeBtn = document.createElement('button');
          closeBtn.className = 'alert-close';
          closeBtn.innerHTML = '&times;';
          closeBtn.onclick = () => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => alert.remove(), 300);
          };
          alert.appendChild(closeBtn);
        }
      });
    }
  };

  // ========================================
  // Loading States
  // ========================================
  const LoadingManager = {
    init() {
      this.showSkeletonLoaders();
      this.hideLoadersOnLoad();
    },

    showSkeletonLoaders() {
      // Show skeleton loaders for async content
      document.querySelectorAll('[data-loading]').forEach(element => {
        element.classList.add('skeleton');
      });
    },

    hideLoadersOnLoad() {
      window.addEventListener('load', () => {
        document.querySelectorAll('.skeleton').forEach(element => {
          element.classList.remove('skeleton');
          element.classList.add('fade-in');
        });
      });
    }
  };

  // ========================================
  // Smooth Scroll
  // ========================================
  const SmoothScroll = {
    init() {
      document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
          const href = this.getAttribute('href');
          if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
              target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
              });
            }
          }
        });
      });
    }
  };

  // ========================================
  // Tooltip System
  // ========================================
  const TooltipManager = {
    init() {
      document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', function() {
          const tooltip = document.createElement('div');
          tooltip.className = 'tooltip';
          tooltip.textContent = this.getAttribute('data-tooltip');
          document.body.appendChild(tooltip);

          const rect = this.getBoundingClientRect();
          tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
          tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';

          setTimeout(() => tooltip.classList.add('show'), 10);

          this._tooltip = tooltip;
        });

        element.addEventListener('mouseleave', function() {
          if (this._tooltip) {
            this._tooltip.classList.remove('show');
            setTimeout(() => this._tooltip.remove(), 200);
          }
        });
      });
    }
  };

  // ========================================
  // Keyboard Navigation
  // ========================================
  const KeyboardNavigation = {
    init() {
      // ESC key to close modals/dropdowns
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          document.querySelectorAll('.modal.show, .dropdown.show').forEach(el => {
            el.classList.remove('show');
          });
        }
      });

      // Tab trap for modals
      document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('keydown', (e) => {
          if (e.key === 'Tab') {
            const focusableElements = modal.querySelectorAll(
              'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (e.shiftKey && document.activeElement === firstElement) {
              e.preventDefault();
              lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
              e.preventDefault();
              firstElement.focus();
            }
          }
        });
      });
    }
  };

  // ========================================
  // Performance Monitoring
  // ========================================
  const PerformanceMonitor = {
    init() {
      // Log page load time
      window.addEventListener('load', () => {
        const loadTime = performance.now();
        console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
        
        // Show warning if load time is slow
        if (loadTime > 3000) {
          console.warn('Page load time is slow. Consider optimization.');
        }
      });
    }
  };

  // ========================================
  // Initialize All Modules
  // ========================================
  document.addEventListener('DOMContentLoaded', () => {
    NavigationManager.init();
    PageTransitions.init();
    FormEnhancements.init();
    CardInteractions.init();
    ButtonInteractions.init();
    AlertManager.init();
    LoadingManager.init();
    SmoothScroll.init();
    TooltipManager.init();
    KeyboardNavigation.init();
    PerformanceMonitor.init();
  });

  // ========================================
  // CSS Animations
  // ========================================
  const style = document.createElement('style');
  style.textContent = `
    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      25% { transform: translateX(-10px); }
      75% { transform: translateX(10px); }
    }

    .ripple {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.6);
      transform: scale(0);
      animation: ripple-animation 0.6s ease-out;
      pointer-events: none;
    }

    @keyframes ripple-animation {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }

    .tooltip {
      position: fixed;
      background: rgba(0, 0, 0, 0.9);
      color: white;
      padding: 0.5rem 0.75rem;
      border-radius: 6px;
      font-size: 0.875rem;
      pointer-events: none;
      z-index: 9999;
      opacity: 0;
      transition: opacity 0.2s;
    }

    .tooltip.show {
      opacity: 1;
    }

    .alert-close {
      position: absolute;
      top: 0.75rem;
      right: 0.75rem;
      background: none;
      border: none;
      font-size: 1.5rem;
      line-height: 1;
      color: inherit;
      opacity: 0.5;
      cursor: pointer;
      transition: opacity 0.2s;
    }

    .alert-close:hover {
      opacity: 1;
    }

    body {
      opacity: 1;
      transition: opacity 0.2s ease;
    }
  `;
  document.head.appendChild(style);

})();
