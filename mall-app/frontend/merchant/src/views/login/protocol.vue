<template>
  <div class="create-pdf">
    <div class="pdf" ref="pdfView">
      <iframe :src="url" width="100%" height="100%" frameborder="0"></iframe>
    </div>
    <div class="close" @click="closeProtocol">
      <i class="el-icon-close" style="font-size: 36px;"></i>
    </div>
  </div>
</template>

<script>  import pdf from 'vue-pdf'
import {mapGetters} from "vuex";
import defaultSettings from "@/settings";

export default {
  name: 'Home',
  components: {
    pdf
  },
  data() {
    return {
      url: "/pact/",
    }
  },
  computed: {
    ...mapGetters(['userInfo']),
  },
  mounted() {

    //如果是开发环境
    if (process.env.NODE_ENV === 'development') {
      this.url = 'https://thsjbvh.site'
    } else {
      //当前域名
      this.url = window.location.origin
    }
    console.log(window.location.origin)
    //this.url 加上token参数
    let token = localStorage.getItem('token')
    this.url += `/www/#/login-agreement?token=${token}&lang=${this.$store.getters.lang}&name=${defaultSettings.projectTitle}`
    window.closePopup = () => {
      this.closeProtocol()
    }
  },
  methods: {
    closeProtocol() {
      this.$emit('closeProtocol')
    },
  }
}
</script>
<style lang="scss">
//当前组件设置成全屏弹窗
.create-pdf {
  width: 100%;
  height: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000000;
  overflow: hidden;

  &::after {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }

  .pdf {
    width: 100%;
    height: 100%;
    position: relative;
    z-index: 1000001;
    top: 0;
    left: 0;
    overflow-y: auto;
    padding: 0;
    display: flex;
    justify-content: center;
  }

  .close {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 50px;
    height: 50px;
    cursor: pointer;
    z-index: 1000002;
    background-color: rgba(0, 0, 0, 0.3);
    color: #FFFFFF;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 50%;

    &:hover {
      background-color: rgba(0, 0, 0, 0.5);
    }
  }
}

</style>
