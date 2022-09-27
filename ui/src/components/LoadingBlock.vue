<template>
  <div class="text-muted">Loading {{ symbol }}</div>
</template>
<script>
export default {
  methods: {
    animateSymbol() {
      let symbols = ". .. ...".split(" ")
      let i = 0
      setInterval(() => {
        if (i < symbols.length) { i++ } else { i = 0 }
        this.symbol = symbols[i]
      }, 300)
    }
  },
  data() {
    return {
      symbol: ""
    }
  },
  mounted() {
    this.animateSymbol()
  }
}
</script>

