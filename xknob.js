'use strict';

if (!window.XKnob) {
	(function() {

		// Convenience functions to sanitize numbers.
		var float_or_default = function(x, def) {
			x = parseFloat(x);
			return isNaN(x) ? def : x;
		};
		var int_or_default = function(x, def) {
			x = parseInt(x, 10);
			return isNaN(x) ? def : x;
		};

		////////////////////
		// Global internal variables for UI handling.

		// A XKnob element if one is being dragged right now.
		//
		// Limitation: only one can be changed at the same time.
		//
		// This limitation is not a problem on mouse-driven interfaces, as
		// there is only a single mouse (well, on most systems anyway).
		//
		// For multi-touch interfaces, this code should be rewritten to support
		// multiple knobs being changed at the same time.
		var xknob_being_dragged = null;

		// The mouse (or touch) angle from the last event. Used to calculate
		// the direction (CW or CCW).
		var xknob_drag_previous_angle = null;

		// The (proposed, before applying min/max/divisions) value from the
		// last event.
		var xknob_drag_previous_value = null;

		// The initial value upon starting to drag the knob. Used to decide if
		// 'change' event should be fired.
		var xknob_drag_initial_value = null;

		////////////////////
		// Event handling functions.

		var add_listeners_to_document = function(elem) {
			if (elem instanceof HTMLElement) {
				elem = elem.ownerDocument;
			}
			// Duplicate event listeners are discarded.
			elem.addEventListener('mouseup', stop_dragging);
			elem.addEventListener('mousemove', drag_rotate);
			elem.addEventListener('touchend', stop_dragging);
			elem.addEventListener('touchmove', drag_rotate);
		}
		var remove_listeners_from_document = function(elem) {
			if (elem instanceof HTMLElement) {
				elem = elem.ownerDocument;
			}
			elem.removeEventListener('mouseup', stop_dragging);
			elem.removeEventListener('mousemove', drag_rotate);
			elem.removeEventListener('touchend', stop_dragging);
			elem.removeEventListener('touchmove', drag_rotate);
		}

		// Should be attached to '.knob_gfx'.
		var start_dragging = function(ev) {
			remove_listeners_from_document(ev.target);
			xknob_being_dragged = null;

			// Only handling clicks with the left mouse button.
			if (ev.type === 'mousedown' && ev.button !== 0) {
				return;
			}

			// Finding the XKnob element.
			// ev.target is where the event was originated.
			// ev.currentTarget is where the event listener was attached.
			var shadow_root = ev.currentTarget;
			while (shadow_root && !(shadow_root instanceof ShadowRoot)) {
				shadow_root = shadow_root.parentNode;
			}
			if (!shadow_root) return;
			var xknob = shadow_root.host;
			if (!xknob) return;

			// No reaction if the element is disabled or readonly.
			if (xknob.disabled || xknob.readonly) {
				// Should we call preventDefault/stopPropagation here?
				return;
			}

			// Actual event handling.
			ev.preventDefault();
			ev.stopPropagation();
			xknob_being_dragged = xknob;
			xknob_drag_previous_angle = xknob._get_mouse_angle(ev);
			xknob_drag_previous_value = xknob.value;
			xknob_drag_initial_value = xknob.value;

			add_listeners_to_document(xknob);

			// Giving the element focus to enable keyboard events.
			// We need to do this here because we called preventDefault() and
			// stopPropagation().
			xknob.focus();
		}

		// Should be attached to the document, because this event may happen
		// outside of XKnob.
		var stop_dragging = function(ev) {
			if (!xknob_being_dragged) {
				remove_listeners_from_document(ev.target);
				return;
			}

			if (xknob_being_dragged.disabled || xknob_being_dragged.readonly) {
				remove_listeners_from_document(ev.target);
				return;
			}

			if (xknob_drag_initial_value !== xknob_being_dragged.value) {
				xknob_being_dragged.dispatchEvent(new Event('change', {
					'bubbles': true,
					'cancelable': false
				}));
			}

			remove_listeners_from_document(ev.target);
			xknob_being_dragged = null;
		}

		// Should be attached to the document, because this event may happen
		// outside of XKnob.
		var drag_rotate = function(ev) {
			if (!xknob_being_dragged) {
				remove_listeners_from_document(ev.target);
				return;
			}

			if (xknob_being_dragged.disabled || xknob_being_dragged.readonly) {
				remove_listeners_from_document(ev.target);
				return;
			}

			var new_angle = xknob_being_dragged._get_mouse_angle(ev);
			var old_angle = xknob_drag_previous_angle;
			xknob_drag_previous_angle = new_angle;

			var delta_angle = new_angle - old_angle;
			if (delta_angle < 0) {
				// Because this is a circle
				delta_angle += Math.PI * 2;
			}
			if (delta_angle > Math.PI) {
				// Converting from 0..360 to -180..180.
				delta_angle -= Math.PI * 2;
			}
			console.assert(delta_angle >= -Math.PI && delta_angle <= Math.PI, {'delta_angle': delta_angle, 'old_angle': old_angle, 'new_angle': new_angle});

			var delta_value = delta_angle / Math.PI / 2;
			var new_proposed_value = xknob_drag_previous_value + delta_value;
			var old_actual_value = xknob_being_dragged.value;

			xknob_being_dragged.value = new_proposed_value;

			// The .value setter changes the xknob_drag_previous_value variable
			// (in case the setter was implicitly called by the user).
			// Here, however, we need xknob_drag_previous_value set to this
			// specific value, so we overwrite it.
			xknob_drag_previous_value = new_proposed_value;

			var new_actual_value = xknob_being_dragged.value;
			if (old_actual_value !== new_actual_value) {
				xknob_being_dragged.dispatchEvent(new Event('input', {
					'bubbles': true,
					'cancelable': false
				}));
			}
		}

		// Keyboard support when receiving focus.
		var keypress_handler = function(ev) {
			if (ev.target.disabled) {
				return;
			}

			// Some constants.
			var STEP_SIZE_SMALL = 1;  // For Arrows.
			var STEP_SIZE_MEDIUM = 2;  // For PageUp/PageDown.
			var STEP_SIZE_EXTREME = 3;  // For Home/End.

			var step_size = null;
			var step_direction = null;

			// ev.code and ev.key are new to DOM 3 Events:
			// https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/code
			// https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/key

			// If I remap my keyboard (e.g. I've remapped Caps Lock to be
			// Escape), then ev.key shows the remapped value (e.g. Escape),
			// while ev.code shows the actual physical key (e.g. Caps Lock).
			//
			// Also, if NumLock is off, numpad keys return their alternate
			// value in ev.key (e.g. ArrowUp), and the actual physical key in
			// ev.code (e.g. Numpad8).
			//
			// For this component, ev.key makes more sense than ev.code, as we
			// are interested in the logical value/action, and not the physical
			// key location.

			switch (ev.key) {
				// The same direction/orientation as <input type="range">.
				case 'Home':
				case 'PageDown':
				case 'ArrowLeft':
				case 'ArrowDown':
					step_direction = -1;
					break;
				case 'End':
				case 'PageUp':
				case 'ArrowRight':
				case 'ArrowUp':
					step_direction = +1;
					break;
				default:
					return;
			}
			switch (ev.key) {
				case 'Home':
				case 'End':
					step_size = STEP_SIZE_EXTREME;
					break;
				case 'PageUp':
				case 'PageDown':
					step_size = STEP_SIZE_MEDIUM;
					break;
				case 'ArrowRight':
				case 'ArrowLeft':
				case 'ArrowDown':
				case 'ArrowUp':
					step_size = STEP_SIZE_SMALL;
					break;
				default:
					return;
			}

			// Sanity check.
			if (step_size === null || step_direction === null) {
				console.error('This should not happen! step_size=' + step_size + ', step_direction=' + step_direction);
				return;
			}

			ev.preventDefault();
			//ev.stopPropagation();

			// Read-only will receive and process the events, but won't change
			// the value.
			if (ev.target.readonly) {
				return;
			}

			var initial_value = ev.target.value;

			if (step_size === STEP_SIZE_EXTREME) {
				if (step_direction < 0) {
					if (ev.target.min !== null) {
						ev.target.value = ev.target.min;
					}
				} else if (step_direction > 0) {
					if (ev.target.max !== null) {
						ev.target.value = ev.target.max;
					}
				}
			} else if (step_size === STEP_SIZE_MEDIUM) {
				var divisions = ev.target.divisions;
				var step = 1.0 / 8;
				// Finding a step amount near 45deg:
				if (divisions >= 2) {
					step = Math.round(step * divisions) / divisions;
					// In case the previous expression evaluated to zero.
					step = Math.max(step, 1.0 / divisions);
				}
				ev.target.value += step * step_direction;
			} else if (step_size === STEP_SIZE_SMALL) {
				var divisions = ev.target.divisions;
				var step = 1.0 / 64;
				if (divisions >= 2) {
					step = 1.0 / divisions;
				}
				ev.target.value += step * step_direction;
			} else {
				console.error('This should not happen! Unknown step_size: ' + step_size);
			}

			if (initial_value !== ev.target.value) {
				ev.target.dispatchEvent(new Event('input', {
					'bubbles': true,
					'cancelable': false
				}));
				ev.target.dispatchEvent(new Event('change', {
					'bubbles': true,
					'cancelable': false
				}));

				// Trying to improve the corner-case of someone dragging the
				// control at same time as using keyboard.
				if (xknob_being_dragged) {
					xknob_drag_initial_value = ev.target.value;
				}
			}
		}

		////////////////////
		// The actual XKnob object.
		class XKnob extends HTMLElement {
			static get observedAttributes() {
				return ['min', 'max', 'step', 'value', 'disabled', 'readonly'];
			}

			constructor() {
				super();
				this.attachShadow({ mode: 'open' });
				this._min = 0;
				this._max = 1;
				this._step = 0.01;
				this._value = 0;
						this._disabled = false;
						this._readonly = false;
				this._dragging = false;
				this._center = 24;
				this._radius = 22;
				this._lastAngle = 0;
				this._rotation = 0;
				this._render();
			}

			connectedCallback() {
				this._upgradeProperty('value');
				this._upgradeProperty('min');
				this._upgradeProperty('max');
				this._upgradeProperty('step');
				this._upgradeProperty('disabled');
				this._upgradeProperty('readonly');
				this._addEventListeners();
				this._update();
						}

			attributeChangedCallback(name, oldValue, newValue) {
				if (oldValue === newValue) return;
				switch (name) {
					case 'min': this._min = parseFloat(newValue); break;
					case 'max': this._max = parseFloat(newValue); break;
					case 'step': this._step = parseFloat(newValue); break;
					case 'value': this.value = parseFloat(newValue); break;
					case 'disabled': this._disabled = newValue !== null; break;
					case 'readonly': this._readonly = newValue !== null; break;
				}
				this._update();
			}

			get value() { return this._value; }
			set value(val) {
				const v = this._clamp(this._stepRound(parseFloat(val)));
				if (v !== this._value) {
					this._value = v;
					this.setAttribute('value', v);
					this._update();
					this.dispatchEvent(new Event('input', { bubbles: true }));
					}
			}
			get min() { return this._min; }
			set min(val) { this._min = parseFloat(val); this.setAttribute('min', val); this._update(); }
			get max() { return this._max; }
			set max(val) { this._max = parseFloat(val); this.setAttribute('max', val); this._update(); }
			get step() { return this._step; }
			set step(val) { this._step = parseFloat(val); this.setAttribute('step', val); this._update(); }
			get disabled() { return this._disabled; }
			set disabled(val) { this._disabled = !!val; this._update(); }
			get readonly() { return this._readonly; }
			set readonly(val) { this._readonly = !!val; this._update(); }

			_upgradeProperty(prop) {
				if (this.hasOwnProperty(prop)) {
					let value = this[prop];
					delete this[prop];
					this[prop] = value;
				}
			}

			_clamp(val) {
				return Math.max(this._min, Math.min(this._max, val));
			}
			_stepRound(val) {
				if (!isFinite(this._step) || this._step <= 0) return val;
				return Math.round((val - this._min) / this._step) * this._step + this._min;
						}

			_render() {
				this.shadowRoot.innerHTML = `
					<style>
						:host { 
							display: inline-block; 
							width: 48px; 
							height: 48px; 
							pointer-events: none;
						}
						svg { 
							width: 100%; 
							height: 100%; 
							display: block; 
							pointer-events: none;
						}
						.knob-bg { 
							transition: fill 0.2s; 
							fill: #e5e5e5;
							stroke: #b0b0b0;
							stroke-width: 1.5;
							filter: drop-shadow(0 2px 6px rgba(0,0,0,0.10));
						}
						.knob-indicator { 
							transition: stroke 0.2s; 
							stroke: #ff6a1a;
							stroke-width: 4;
							stroke-linecap: round;
							filter: drop-shadow(0 0 2px #ff6a1a88);
						}
						.knob-dot { 
							transition: fill 0.2s; 
							fill: #ff6a1a;
							filter: drop-shadow(0 0 4px #ff6a1a88);
						}
						.knob-indicator-group {
							pointer-events: auto;
							cursor: pointer;
						}
					</style>
					<svg viewBox="0 0 48 48">
						<circle class="knob-bg" cx="24" cy="24" r="22"/>
						<g class="knob-indicator-group"></g>
						<circle class="knob-dot" cx="24" cy="24" r="4"/>
					</svg>



					<svg width="115" height="121" viewBox="0 0 115 121" fill="none" xmlns="http://www.w3.org/2000/svg">
						<g id="Knob">
							<g id="Base" filter="url(#filter0_ddd_427_2080)">
								<circle cx="62.5" cy="68.5" r="19.5" fill="url(#paint0_linear_427_2080)" />
							</g>
							<g id="Knurled" filter="url(#filter1_di_427_2080)">
								<path
									d="M60.8284 49.8331C61.9195 49.5107 63.0805 49.5107 64.1716 49.8331V49.8331C64.7411 50.0015 65.3328 50.0828 65.9267 50.0744V50.0744C67.0643 50.0582 68.1822 50.3715 69.1458 50.9763V50.9763C69.6489 51.2921 70.1967 51.53 70.7708 51.6821V51.6821C71.8705 51.9735 72.8625 52.5768 73.6272 53.4192V53.4192C74.0264 53.8589 74.4897 54.2359 75.0015 54.5372V54.5372C75.9818 55.1145 76.7743 55.963 77.2833 56.9805V56.9805C77.5491 57.5116 77.8935 57.9996 78.305 58.4279V58.4279C79.0933 59.2483 79.6274 60.2791 79.8431 61.3962V61.3962C79.9556 61.9793 80.1557 62.5421 80.4364 63.0655V63.0655C80.974 64.0681 81.2102 65.2049 81.1165 66.3387V66.3387C81.0676 66.9306 81.1084 67.5265 81.2374 68.1062V68.1062C81.4847 69.2167 81.4054 70.375 81.0093 71.4415V71.4415C80.8025 71.9983 80.681 72.5831 80.6488 73.1761V73.1761C80.5873 74.3121 80.1985 75.4061 79.5293 76.3262V76.3262C79.18 76.8065 78.9052 77.3368 78.7142 77.8992V77.8992C78.3485 78.9765 77.6789 79.925 76.7863 80.6304V80.6304C76.3203 80.9987 75.9127 81.4352 75.5771 81.9252V81.9252C74.9342 82.8639 74.0336 83.5966 72.9838 84.035V84.035C72.4358 84.2639 71.9254 84.5742 71.4701 84.9555V84.9555C70.5978 85.6859 69.5329 86.1485 68.4037 86.2874V86.2874C67.8143 86.3599 67.2391 86.5211 66.6978 86.7654V86.7654C65.6608 87.2334 64.5106 87.3915 63.3858 87.2206V87.2206C62.7986 87.1314 62.2014 87.1314 61.6142 87.2206V87.2206C60.4894 87.3915 59.3392 87.2334 58.3022 86.7654V86.7654C57.7609 86.5211 57.1857 86.3599 56.5963 86.2874V86.2874C55.4671 86.1485 54.4022 85.6859 53.5299 84.9555V84.9555C53.0746 84.5742 52.5643 84.2639 52.0162 84.035V84.035C50.9664 83.5966 50.0658 82.8639 49.4229 81.9252V81.9252C49.0873 81.4352 48.6797 80.9987 48.2137 80.6304V80.6304C47.3211 79.925 46.6515 78.9765 46.2858 77.8992V77.8992C46.0948 77.3368 45.8201 76.8065 45.4707 76.3262V76.3262C44.8015 75.4061 44.4127 74.3121 44.3512 73.1761V73.1761C44.319 72.5831 44.1975 71.9983 43.9907 71.4415V71.4415C43.5946 70.375 43.5153 69.2167 43.7626 68.1062V68.1062C43.8916 67.5265 43.9324 66.9306 43.8835 66.3387V66.3387C43.7898 65.2049 44.026 64.0681 44.5637 63.0655V63.0655C44.8443 62.5421 45.0444 61.9793 45.1569 61.3962V61.3962C45.3726 60.2791 45.9067 59.2483 46.695 58.4279V58.4279C47.1065 57.9996 47.4509 57.5116 47.7167 56.9805V56.9805C48.2257 55.963 49.0182 55.1145 49.9985 54.5372V54.5372C50.5103 54.2359 50.9736 53.8589 51.3728 53.4192V53.4192C52.1375 52.5768 53.1295 51.9735 54.2292 51.6821V51.6821C54.8033 51.53 55.3511 51.2921 55.8542 50.9763V50.9763C56.8178 50.3715 57.9357 50.0582 59.0733 50.0744V50.0744C59.6672 50.0828 60.2589 50.0015 60.8284 49.8331V49.8331Z"
									fill="url(#paint1_linear_427_2080)" />
							</g>
							<g id="knob-indicator-group" filter="url(#filter2_di_427_2080)"></g>
						</g>
						<defs>
							<filter id="filter0_ddd_427_2080" x="-5.99999" y="0" width="121" height="121" filterUnits="userSpaceOnUse"
								color-interpolation-filters="sRGB">
								<feFlood flood-opacity="0" result="BackgroundImageFix" />
								<feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
									result="hardAlpha" />
								<feMorphology radius="9" operator="dilate" in="SourceAlpha" result="effect1_dropShadow_427_2080" />
								<feOffset dx="-8" dy="-8" />
								<feGaussianBlur stdDeviation="16" />
								<feComposite in2="hardAlpha" operator="out" />
								<feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.4 0" />
								<feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_427_2080" />
								<feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
									result="hardAlpha" />
								<feOffset dx="8" dy="8" />
								<feGaussianBlur stdDeviation="8" />
								<feComposite in2="hardAlpha" operator="out" />
								<feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.35 0" />
								<feBlend mode="normal" in2="effect1_dropShadow_427_2080" result="effect2_dropShadow_427_2080" />
								<feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
									result="hardAlpha" />
								<feOffset dx="2" dy="2" />
								<feGaussianBlur stdDeviation="2" />
								<feComposite in2="hardAlpha" operator="out" />
								<feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.35 0" />
								<feBlend mode="normal" in2="effect2_dropShadow_427_2080" result="effect3_dropShadow_427_2080" />
								<feBlend mode="normal" in="SourceGraphic" in2="effect3_dropShadow_427_2080" result="shape" />
							</filter>
							<filter id="filter1_di_427_2080" x="43.6216" y="49.5913" width="39.7567" height="39.6962"
								filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
								<feFlood flood-opacity="0" result="BackgroundImageFix" />
								<feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
									result="hardAlpha" />
								<feOffset dx="1" dy="1" />
								<feGaussianBlur stdDeviation="0.5" />
								<feComposite in2="hardAlpha" operator="out" />
								<feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.4 0" />
								<feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_427_2080" />
								<feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_427_2080" result="shape" />
								<feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
									result="hardAlpha" />
								<feOffset dx="1" dy="1" />
								<feGaussianBlur stdDeviation="0.5" />
								<feComposite in2="hardAlpha" operator="arithmetic" k2="-1" k3="1" />
								<feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.8 0" />
								<feBlend mode="normal" in2="shape" result="effect2_innerShadow_427_2080" />
							</filter>
							<filter id="filter2_di_427_2080" x="53.8522" y="49" width="19.2957" height="30.1475"
								filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
								<feFlood flood-opacity="0" result="BackgroundImageFix" />
								<feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
									result="hardAlpha" />
								<feOffset dx="1" dy="1" />
								<feGaussianBlur stdDeviation="0.5" />
								<feComposite in2="hardAlpha" operator="out" />
								<feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.8 0" />
								<feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_427_2080" />
								<feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_427_2080" result="shape" />
								<feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
									result="hardAlpha" />
								<feOffset dx="2" dy="2" />
								<feGaussianBlur stdDeviation="2" />
								<feComposite in2="hardAlpha" operator="arithmetic" k2="-1" k3="1" />
								<feColorMatrix type="matrix" values="0 0 0 0 0.545098 0 0 0 0 0.145098 0 0 0 0 0.105882 0 0 0 0.9 0" />
								<feBlend mode="normal" in2="shape" result="effect2_innerShadow_427_2080" />
							</filter>
							<filter id="filter3_di_427_2080" x="53.8522" y="59.8522" width="23.2957" height="23.2957"
								filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
								<feFlood flood-opacity="0" result="BackgroundImageFix" />
								<feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
									result="hardAlpha" />
								<feOffset dx="1" dy="1" />
								<feGaussianBlur stdDeviation="0.5" />
								<feComposite in2="hardAlpha" operator="out" />
								<feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.8 0" />
								<feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_427_2080" />
								<feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_427_2080" result="shape" />
								<feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
									result="hardAlpha" />
								<feOffset dx="6" dy="6" />
								<feGaussianBlur stdDeviation="6" />
								<feComposite in2="hardAlpha" operator="arithmetic" k2="-1" k3="1" />
								<feColorMatrix type="matrix" values="0 0 0 0 0.545098 0 0 0 0 0.145098 0 0 0 0 0.105882 0 0 0 0.9 0" />
								<feBlend mode="normal" in2="shape" result="effect2_innerShadow_427_2080" />
							</filter>
							<filter id="filter4_f_427_2080" x="55.2782" y="42.9652" width="14.1043" height="24.6174"
								filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
								<feFlood flood-opacity="0" result="BackgroundImageFix" />
								<feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape" />
								<feGaussianBlur stdDeviation="2" result="effect1_foregroundBlur_427_2080" />
							</filter>
							<filter id="filter5_f_427_2080" x="56.6695" y="40.9652" width="18.7826" height="26.5826"
								filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
								<feFlood flood-opacity="0" result="BackgroundImageFix" />
								<feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape" />
								<feGaussianBlur stdDeviation="3" result="effect1_foregroundBlur_427_2080" />
							</filter>
							<linearGradient id="paint0_linear_427_2080" x1="48.8673" y1="55.2124" x2="75.6151" y2="81.9602"
								gradientUnits="userSpaceOnUse">
								<stop stop-color="#E7E7E7" />
								<stop offset="1" stop-color="#C2C2C4" />
							</linearGradient>
							<linearGradient id="paint1_linear_427_2080" x1="62.5" y1="49.3391" x2="62.5" y2="87.6609"
								gradientUnits="userSpaceOnUse">
								<stop stop-color="#C7C7C9" />
								<stop offset="1" stop-color="#C5C5C7" />
							</linearGradient>
							<radialGradient id="paint2_radial_427_2080" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse"
								gradientTransform="translate(68.0957 74.0957) rotate(-135) scale(9.83186)">
								<stop stop-color="#FEDAC3" />
								<stop offset="0.484375" stop-color="#FF9C57" />
								<stop offset="1" stop-color="#F9601B" />
							</radialGradient>
							<linearGradient id="paint3_linear_427_2080" x1="62.3304" y1="60.3609" x2="62.3304" y2="64.2609"
								gradientUnits="userSpaceOnUse">
								<stop />
								<stop offset="1" stop-opacity="0" />
							</linearGradient>
							<linearGradient id="paint4_linear_427_2080" x1="59.2782" y1="55.4435" x2="65.3826" y2="55.4435"
								gradientUnits="userSpaceOnUse">
								<stop stop-color="#D93E13" />
								<stop offset="1" stop-color="#FF6924" />
							</linearGradient>
						</defs>
					</svg>
					
				`;
				this._svg = this.shadowRoot.querySelector('svg');
				this._indicatorGroup = this.shadowRoot.querySelector('.knob-indicator-group');
			}

			_addEventListeners() {
				this._svg.addEventListener('mousedown', this._onPointerDown.bind(this));
				this._svg.addEventListener('touchstart', this._onPointerDown.bind(this), { passive: false });
				window.addEventListener('mousemove', this._onPointerMove.bind(this));
				window.addEventListener('touchmove', this._onPointerMove.bind(this), { passive: false });
				window.addEventListener('mouseup', this._onPointerUp.bind(this));
				window.addEventListener('touchend', this._onPointerUp.bind(this));
			}

			_getAngleFromCenter(x, y) {
				const rect = this._svg.getBoundingClientRect();
				const cx = rect.left + rect.width / 2;
				const cy = rect.top + rect.height / 2;
				return Math.atan2(y - cy, x - cx);
			}

			_onPointerDown(e) {
				if (this._disabled || this._readonly) return;
				e.preventDefault();
				this._dragging = true;
				const { clientX, clientY } = e.touches ? e.touches[0] : e;
				this._lastAngle = this._getAngleFromCenter(clientX, clientY);
				this._startValue = this._value;
				this._rotation = 0;
						}

			_onPointerMove(e) {
				if (!this._dragging) return;
				e.preventDefault();
				const { clientX, clientY } = e.touches ? e.touches[0] : e;
				const angle = this._getAngleFromCenter(clientX, clientY);
				let delta = angle - this._lastAngle;
				// Normalize delta to [-PI, PI]
				if (delta > Math.PI) delta -= 2 * Math.PI;
				if (delta < -Math.PI) delta += 2 * Math.PI;
				this._rotation += delta;
				this._lastAngle = angle;
				// Map rotation to value
				const range = this._max - this._min;
				let newValue = this._startValue + (this._rotation / (2 * Math.PI)) * range;
				newValue = this._clamp(this._stepRound(newValue));
				if (newValue !== this._value) {
					this._value = newValue;
					this.setAttribute('value', newValue);
					this._update();
					this.dispatchEvent(new Event('input', { bubbles: true }));
				}
			}

			_onPointerUp(e) {
				if (!this._dragging) return;
				this._dragging = false;
				this.dispatchEvent(new Event('change', { bubbles: true }));
			}

			_update() {
				// Draw indicator arc and line
				if (!this._indicatorGroup) return;
				const angle = ((this._value - this._min) / (this._max - this._min)) * 2 * Math.PI - Math.PI / 2;
				const r = 16;
				// Use the correct center coordinates for the orange knob SVG
				const centerX = 33;
				const centerY = 55;
				const x2 = centerX + r * Math.cos(angle);
				const y2 = centerY + r * Math.sin(angle);
				// Arc (background) OLD CODE
				// this._indicatorGroup.innerHTML = `
				// 	<path class="knob-indicator" d="M24,24 L${x2},${y2}"/>
				// `;
				// Arc (background) NEW CODE
				const deg = ((this._value - this._min) / (this._max - this._min)) * 360; // in degrees
				this._indicatorGroup.innerHTML = `
					<g transform="rotate(${deg}, ${centerX}, ${centerY})">
						<mask id="mask0_427_2080" style="mask-type:alpha" maskUnits="userSpaceOnUse" x="24" y="20" width="19" height="29">
							<path id="Indent Mask"
								d="M33.3307 20C34.6417 20.0001 35.7047 21.063 35.7047 22.374V30.5127C35.7047 30.8485 35.8902 31.1803 36.2092 31.2854C39.6582 32.4222 42.1481 35.6702 42.1481 39.5C42.1481 44.2761 38.2757 48.1475 33.4996 48.1475C28.7237 48.1473 24.8522 44.2759 24.8522 39.5C24.8522 35.8182 27.1535 32.6751 30.3958 31.4277C30.756 31.2892 30.9567 30.8986 30.9567 30.5127V22.374C30.9567 21.0629 32.0196 20 33.3307 20Z"
								fill="black" />
						</mask>
						<g mask="url(#mask0_427_2080)">
							<g id="Circular Indent" filter="url(#filter3_di_427_2080)">
								<circle cx="33" cy="39.5" r="8.64783" fill="url(#paint2_radial_427_2080)" />
							</g>
							<g id="Line">
								<mask id="mask1_427_2080" style="mask-type:alpha" maskUnits="userSpaceOnUse" x="30" y="20" width="6" height="16">
									<rect id="Line Mask" x="30.9565" y="20" width="4.74783" height="15.2609" rx="2.37391" fill="url(#paint3_linear_427_2080)" />
								</mask>
								<g mask="url(#mask1_427_2080)">
									<g id="Rectangle 2" filter="url(#filter4_f_427_2080)">
										<rect x="30.2782" y="17.9652" width="6.10435" height="16.6174" fill="url(#paint4_linear_427_2080)" />
									</g>
									<g id="Rectangle 1" filter="url(#filter5_f_427_2080)">
										<rect x="33.6695" y="17.9652" width="6.78261" height="14.5826" fill="#FFA96C" />
									</g>
								</g>
							</g>
						</g>
					</g>
				`;

				// Update disabled/readonly style
				this._svg.style.opacity = this._disabled ? 0.5 : 1;
				this._svg.style.pointerEvents = this._disabled ? 'none' : 'auto';
			}
		}

		customElements.define('x-knob', XKnob);
	})();
}
