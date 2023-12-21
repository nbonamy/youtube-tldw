
// init vue
var vm = new Vue({
  el: '#app',
  data: {
    models: ['default'],
    langs: ['default'],
    video: null,//'https://www.youtube.com/watch?v=KNTWhNctGZ4',
    info: null,
    lang: 'default',
    model: 'default',
    method: 'prompt',
    verbosity: 'concise',
    response: null,
    hasEmbeds: false,
    isReady: false,
    isLoading: false,
  },
  computed: {
    performance() {
      let perf = this.response?.performance
      return `Total time: ${perf?.total_time} ms / Time to 1st token: ${perf?.time_1st_token} ms / Tokens per sec: ${perf?.tokens_per_sec}`
    }
  },
  methods: {
    unready() {
      this.isReady = false
    },
    loadModels() {
      this.isLoading = true
      axios.get('/models').then(response => {
        this.models = response.data.models
        if (this.models.indexOf('mistral:latest') != -1) this.model = 'mistral:latest'
        else if (this.models.indexOf('llama2:latest') != -1) this.model = 'llama2:latest'
        else this.model = this.models[0]
        this.isLoading = false
      }).catch(_ => {
        this.showError('Models could not be loaded.')
      })
    },
    loadVideoInfo() {
      this.summary = null
      this.hasEmbeds = false
      this.isLoading = true
      axios.get(`/info?video=${this.video}`).then(response => {
        this.info = response.data
        if (response.data.subtitles.length > 0) {
          this.langs = response.data.subtitles
          this.lang = this.langs[0]
        } else {
          this.langs = ['default']
          this.lang = 'default'
        }
        this.isLoading = false
        this.isReady = true
      }).catch(_ => {
        this.isReady = false
        this.showError('Error while getting video info.')
      })
    },
    summarize() {
      this.isLoading = true
      axios.get(`/summarize?video=${this.video}&lang=${this.lang}&model=${this.model}&method=${this.method}&verbosity=${this.verbosity}`).then(response => {
        this.response = response.data
        this.hasEmbeds = (this.method == 'embeddings')
        this.isLoading = false
      }).catch(_ => {
        this.showError('Error while summarizing video.')
      })
    },
    ask() {
      this.isLoading = true
      axios.get(`/ask?question=${this.question}`).then(response => {
        this.response = response.data
        this.isLoading = false
      }).catch(_ => {
        this.showError('Error while asking model.')
      })
    },
    parseDate(dateString) {
      var year = dateString.substring(0, 4);
      var month = dateString.substring(4, 6);
      var day = dateString.substring(6, 8);
      return new Date(year, month - 1, day);
    },
    formatDate(date) {
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    showError(msg) {
      this.isLoading = false
      this.$buefy.dialog.alert({
        title: 'Error',
        message: msg,
        type: 'is-danger',
        hasIcon: true,
        icon: 'alert-circle',
        iconPack: 'mdi'
      })
    }
  },
  mounted() {
    this.loadModels()
  },
})
