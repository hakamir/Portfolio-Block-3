<script setup lang="ts">
import Footer from "@components/layout/footer/Footer.vue";
import AudioPlayer from "@components/AudioPlayer.vue";

</script>

<template>
  <div class="relative min-h-screen flex flex-col">
    <img src="../../assets/img/gallery_0001.webp" alt="Portfolio Image"
         class="fixed inset-0 w-full h-full object-cover -z-20">
    <div class="fixed inset-0 bg-linear-180 from-black/0 to-black -z-10"></div>

    <section class="flex-1 pt-28 pb-16 md:pt-48 px-8 md:px-32 text-white">
      <div class="container mx-auto">
        <h1 class="hero-title text-white text-shadow-[0_0_40px_rgba(0,0,0,1)] font-unbounded mb-36 mt-16 md:mt-0">
          <span>Explore</span>
          <span>a brand new</span>
          <span>Horizon</span>
        </h1>
        <h2 class="font-unbounded text-3xl md:text-5xl mb-8 text-shadow-[0_0_20px_rgba(0,0,0,1)]">Discover my albums</h2>
        <div class="px-4 lg:px-12 py-12 backdrop-blur-sm rounded-3xl border border-white/20 shadow-[0_0_50px_rgba(0,0,0,0.5)] mb-16">
          <h1 class="text-3xl font-unbounded text-shadow-[0_0_10px_rgba(0,0,0,1)]">Deviance - Nex Hominis</h1>
          <div class="flex flex-col mt-16 gap-12 md:px-16">
            <AudioPlayer title="Burden of Silence" src="/audio/nex_hominis/burden_of_silence.mp3"
                         subtitle="Deviance - Nex Hominis"/>
            <AudioPlayer title="Chaos" src="/audio/nex_hominis/chaos.mp3" subtitle="Deviance - Nex Hominis"/>
            <AudioPlayer title="New Horizon" src="/audio/nex_hominis/new_horizon.mp3"
                         subtitle="Deviance - Nex Hominis"/>
            <AudioPlayer title="Raise the Anger" src="/audio/nex_hominis/raise_the_anger.mp3"
                         subtitle="Deviance - Nex Hominis"/>
          </div>
        </div>
        <div class="px-4 lg:px-12 py-12 backdrop-blur-sm rounded-3xl border border-white/20 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
          <h1 class="text-3xl font-unbounded text-shadow-[0_0_10px_rgba(0,0,0,1)]">Deviance - Legion</h1>
          <div class="flex flex-col mt-16 gap-12 md:px-16">
            <AudioPlayer title="Beyond Wasteland" src="/audio/legion/beyond_wasteland.mp3"
                         subtitle="Deviance - Legion"/>
            <AudioPlayer title="The Desolation" src="/audio/legion/the_desolation.mp3" subtitle="Deviance - Legion"/>
            <AudioPlayer title="Legion" src="/audio/legion/legion.mp3" subtitle="Deviance - Legion"/>
            <AudioPlayer title="Armalion" src="/audio/legion/armalion.mp3"
                         subtitle="Deviance - Legion"/>
            <AudioPlayer title="Birth" src="/audio/legion/birth.mp3"
                         subtitle="Deviance - Legion"/>
            <AudioPlayer title="Colossus" src="/audio/legion/colossus.mp3" subtitle="Deviance - Legion"/>
            <AudioPlayer title="Synthetic Breath" src="/audio/legion/synthetic_breath.mp3"
                         subtitle="Deviance - Legion"/>
            <AudioPlayer title="Raise of the Storm" src="/audio/legion/raise_of_the_storm.mp3"
                         subtitle="Deviance - Legion"/>
            <AudioPlayer title="Solitude" src="/audio/legion/solitude.mp3"
                         subtitle="Deviance - Legion"/>
          </div>
        </div>
      </div>
    </section>

    <Footer/>
  </div>
</template>