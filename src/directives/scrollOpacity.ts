/**
 * Vue directive that progressively changes the background opacity of an element
 * based on scroll position within a container.
 *
 * This directive automatically detects the element's background color and applies
 * opacity transitions as the user scrolls, creating smooth fade-in effects.
 *
 * @example
 * // Basic usage with default options
 * <header v-scroll-opacity></header>
 *
 * @example
 * // With custom options
 * <header v-scroll-opacity="{ maxScroll: 500, offset: 200, scrollContainer: 'main' }"></header>
 *
 * @example
 * // Disable on certain pages
 * <header v-scroll-opacity="isHomePage? { maxScroll: 500 }: null"></header>
 */

import type { Directive, DirectiveBinding } from 'vue'

/**
 * Configuration options for the scroll opacity directive
 */
export interface ScrollOpacityOptions {
  /**
   * Maximum scroll distance (in pixels) to reach full opacity (1.0)
   * @default 500
   * @example maxScroll: 300 // Full opacity after scrolling 300px
   */
  maxScroll?: number

  /**
   * Scroll offset (in pixels) before the opacity transition begins
   * @default 0
   * @example offset: 100 // Start transition after 100px of scroll
   */
  offset?: number

  /**
   * CSS selector for the scroll container element
   * @default 'main'
   * @example scrollContainer: '.custom-scroll-container'
   */
  scrollContainer?: string
}

/**
 * Internal handler state stored on the element
 */
interface ScrollOpacityHandler {
  updateOpacity: () => void
  scrollElement: HTMLElement | Window
  options: Required<ScrollOpacityOptions>
  rgb: string
}

/**
 * Vue directive for progressive background opacity based on scroll position
 *
 * Features:
 * - Automatically detects an element's 'background-color'
 * - Smooth opacity transitions (0 to 1) based on scroll
 * - Supports custom scroll containers (useful for snap-scroll layouts)
 * - Reactive to option changes
 * - Proper cleanup on 'unmount'
 *
 * @type {Directive<HTMLElement, ScrollOpacityOptions>}
 */
export const vScrollOpacity: Directive<HTMLElement, ScrollOpacityOptions> = {
  /**
   * Called when the directive is bound to an element
   *
   * @param el - The DOM element the directive is bound to
   * @param binding - Contains the directive's value (options)
   */
  mounted(el: HTMLElement, binding: DirectiveBinding<ScrollOpacityOptions>) {
    // Merge user options with defaults
    const options: Required<ScrollOpacityOptions> = {
      maxScroll: binding.value?.maxScroll ?? 500,
      offset: binding.value?.offset ?? 0,
      scrollContainer: binding.value?.scrollContainer ?? 'main'
    }

    // Get the current computed background color of the element
    const bgColor = window.getComputedStyle(el).backgroundColor

    // Default to black if no color is detected
    let rgb = '0, 0, 0'

    // Extract RGB values from the computed color
    // Matches patterns like: rgb(0, 0, 0) or rgba(0, 0, 0, 0.5)
    const rgbaMatch = bgColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/)
    if (rgbaMatch) {
      // Extract the three RGB values (ignore alpha if present)
      rgb = `${rgbaMatch[1]}, ${rgbaMatch[2]}, ${rgbaMatch[3]}`
    }

    /**
     * Updates the element's background opacity based on the current scroll position
     *
     * Opacity calculation:
     * - Below offset: opacity = 0 (fully transparent)
     * - Between offset and (offset + maxScroll): opacity = 0 to 1 (gradual)
     * - Above (offset + maxScroll): opacity = 1 (fully opaque)
     */
    const updateOpacity = (): void => {
      // Find the scroll container element
      const scrollElement = document.querySelector(options.scrollContainer) as HTMLElement

      // Get the current scroll position
      // Use scrollTop for elements, scrollY for window
      const scrollPosition = scrollElement ? scrollElement.scrollTop : window.scrollY

      // Calculate opacity value between 0 and 1
      // Formula: (scrollPosition - offset) / maxScroll
      // Math.max ensures minimum 0, Math.min ensures maximum 1
      const opacity = Math.min(
        Math.max((scrollPosition - options.offset) / options.maxScroll, 0),
        1
      )

      // Apply the background color with calculated opacity
      // Uses rgba format to preserve RGB while modifying an alpha channel
      el.style.backgroundColor = `rgba(${rgb}, ${opacity})`
    }

    // Apply the initial opacity state and attach the listener after the next frame
    // This ensures the scroll container is fully mounted and scroll position is properly detected
    requestAnimationFrame(() => {
      // Find the element to listen for scroll events
      // Falls back to the window if the selector doesn't match anything
      const scrollElement = document.querySelector(options.scrollContainer) || window

      // Attach a scroll listener to update opacity on every scroll event
      scrollElement.addEventListener('scroll', updateOpacity)

      // Apply the initial opacity state
      updateOpacity()

      // Store handler data on the element for later access in updated/unmounted hooks
      // Using type assertion to bypass TypeScript's index signature restriction
      ;(el as any)._scrollOpacityHandler = {
        updateOpacity,
        scrollElement,
        options,
        rgb
      } as ScrollOpacityHandler
    })
  },

  /**
   * Called when the directive's value changes (reactive updates)
   *
   * This allows the directive to react to route changes or prop updates
   * without remounting the element.
   *
   * @param el - The DOM element the directive is bound to
   * @param binding - Contains the new directive value (options)
   */
  updated(el: HTMLElement, binding: DirectiveBinding<ScrollOpacityOptions>) {
    // Retrieve stored handler from element
    const oldHandler = (el as any)._scrollOpacityHandler as ScrollOpacityHandler | undefined

    // Exit early if no handler exists (shouldn't happen in normal flow)
    if (!oldHandler) return

    // Create a new options object with updated values
    const newOptions: Required<ScrollOpacityOptions> = {
      maxScroll: binding.value?.maxScroll ?? 500,
      offset: binding.value?.offset ?? 0,
      scrollContainer: binding.value?.scrollContainer ?? 'main'
    }

    // Check if any option has changed
    // Only re-initialize if necessary to avoid unnecessary work
    const hasChanged =
      oldHandler.options.maxScroll !== newOptions.maxScroll ||
      oldHandler.options.offset !== newOptions.offset ||
      oldHandler.options.scrollContainer !== newOptions.scrollContainer

    if (hasChanged) {
      // Remove the old scroll listener to prevent memory leaks
      oldHandler.scrollElement.removeEventListener('scroll', oldHandler.updateOpacity)

      // Re-read the background color (it might have changed due to class updates)
      const bgColor = window.getComputedStyle(el).backgroundColor

      // Keep the old RGB if the new color can't be parsed
      let rgb = oldHandler.rgb
      const rgbaMatch = bgColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/)
      if (rgbaMatch) {
        rgb = `${rgbaMatch[1]}, ${rgbaMatch[2]}, ${rgbaMatch[3]}`
      }

      // Create a new update function with updated options
      const updateOpacity = (): void => {
        const scrollElement = document.querySelector(newOptions.scrollContainer) as HTMLElement
        const scrollPosition = scrollElement ? scrollElement.scrollTop : window.scrollY
        const opacity = Math.min(
          Math.max((scrollPosition - newOptions.offset) / newOptions.maxScroll, 0),
          1
        )
        el.style.backgroundColor = `rgba(${rgb}, ${opacity})`
      }

      // Apply the initial state with new options
      updateOpacity()

      // Find scroll element (might have changed if the scrollContainer option changed)
      const scrollElement = document.querySelector(newOptions.scrollContainer) || window

      // Attach new scroll listener
      scrollElement.addEventListener('scroll', updateOpacity);

      // Update stored handler with new values
      (el as any)._scrollOpacityHandler = {
        updateOpacity,
        scrollElement,
        options: newOptions,
        rgb
      } as ScrollOpacityHandler
    }
  },

  /**
   * Called when the directive is unbound from an element (cleanup)
   *
   * Critical for preventing memory leaks by removing event listeners
   * and cleaning up stored references.
   *
   * @param el - The DOM element the directive was bound to
   */
  unmounted(el: HTMLElement) {
    // Retrieve stored handler
    const handler = (el as any)._scrollOpacityHandler as ScrollOpacityHandler | undefined

    if (handler) {
      // Remove the scroll event listener to prevent memory leaks
      handler.scrollElement.removeEventListener('scroll', handler.updateOpacity)

      // Reset inline background color style
      el.style.backgroundColor = ''

      // Delete stored handler from element
      delete (el as any)._scrollOpacityHandler
    }
  }
}