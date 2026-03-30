import type { Directive, DirectiveBinding } from 'vue'

interface WaveOptions {
  y?: number
  delayIn?: number
  delayOut?: number
  scale?: number
}

export const vWave: Directive<HTMLElement, WaveOptions> = {
  mounted(el: HTMLElement, binding: DirectiveBinding<WaveOptions>) {
    const options = {
      y: binding.value?.y ?? 5,
      delayIn: binding.value?.delayIn ?? 15,
      delayOut: binding.value?.delayOut ?? 5,
      scale: binding.value?.scale ?? 1.15
    }

    const letters = el.textContent?.split("") || []
    el.textContent = ""

    letters.forEach((letter, i) => {
      if (letter === " ") {
        el.appendChild(document.createTextNode(" "))
        return
      }
      const span = document.createElement("span")
      span.textContent = letter
      span.classList.add("inline-block", "transform", "transition-transform", "duration-300")
      span.dataset.index = String(i)
      el.appendChild(span)
    })

    const spans = el.querySelectorAll("span")
    let timeouts: number[] = []

    const animateIn = () => {
      timeouts.forEach(t => clearTimeout(t))
      timeouts = []
      spans.forEach((span, i) => {
        const t = window.setTimeout(() => {
          ;(span as HTMLElement).style.transform = `translateY(-${options.y}px) scale(${options.scale})`
        }, i * options.delayIn)
        timeouts.push(t)
      })
    }

    const animateOut = () => {
      timeouts.forEach(t => clearTimeout(t))
      timeouts = []
      spans.forEach((span, i) => {
        const t = window.setTimeout(() => {
          ;(span as HTMLElement).style.transform = `translateY(0) scale(1)`
        }, i * options.delayOut)
        timeouts.push(t)
      })
    }

    el.addEventListener("mouseenter", animateIn)
    el.addEventListener("mouseleave", animateOut)

    // Stocker les handlers et timeouts pour cleanup
    ;(el as any)._waveHandlers = { animateIn, animateOut, timeouts }
  },

  unmounted(el: HTMLElement) {
    const handlers = (el as any)._waveHandlers
    if (handlers) {
      // Nettoyer les timeouts
      handlers.timeouts.forEach((t: number) => clearTimeout(t))

      // Retirer les event listeners
      el.removeEventListener("mouseenter", handlers.animateIn)
      el.removeEventListener("mouseleave", handlers.animateOut)

      delete (el as any)._waveHandlers
    }
  }
}
