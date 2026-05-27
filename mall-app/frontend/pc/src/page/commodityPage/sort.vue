<template>
  <div class="sort commodity-content-title flex-start">
    <h2
      @click="sortEvent('complex')"
      style="cursor: pointer; user-select: none"
      :class="[currentType == 'complex' && 'checked']"
      v-if="itemname !== 'Argos' || itemname !== 'ArgosArgos'"
    >
      {{ this.$t("message.home.complex" /**复杂 */) }}
    </h2>
    <ul class="flex-start">
      <li
        class="flex-start"
        @click.stop="sortEvent('isHot', sortParameter.isHot == 2 ? 1 : 2)"
      >
        <span :class="[currentType == 'isHot' && 'checked']">{{
          $t("message.home.sales")
        }}</span>
        <div class="flex-start">
          <div class="sort-icon sort-icon-up">
            <i
              :class="{
                'el-icon-caret-top': true,
                'sort-active': sortParameter.isHot === 1,
              }"
            ></i>
          </div>
          <div class="sort-icon sort-icon-down">
            <i
              :class="{
                'el-icon-caret-bottom': true,
                'sort-active': sortParameter.isHot === 2,
              }"
            ></i>
          </div>
        </div>
      </li>
      <li
        class="flex-start"
        @click.stop="sortEvent('isPrice', sortParameter.isPrice == 2 ? 1 : 2)"
      >
        <span :class="[currentType == 'isPrice' && 'checked']">{{
          this.$t("message.home.price" /** 价格*/)
        }}</span>
        <div class="flex-start">
          <div class="sort-icon sort-icon-up">
            <i
              :class="{
                'el-icon-caret-top': true,
                'sort-active': sortParameter.isPrice == 1,
              }"
            ></i>
          </div>
          <div class="sort-icon sort-icon-down">
            <i
              :class="{
                'el-icon-caret-bottom': true,
                'sort-active': sortParameter.isPrice == 2,
              }"
            ></i>
          </div>
        </div>
      </li>
      
      <li
        v-if="itemname !== 'Argos'||itemname !== 'ArgosShop'"
        class="flex-start"
        @click="sortEvent('isNew', sortParameter.isNew == 2 ? 1 : 2)"
      >
        <span :class="[currentType == 'isNew' && 'checked']">{{
          $t("message.home.upNew")
        }}</span>
        <div class="flex-start">
          <div class="sort-icon sort-icon-up">
            <i
              :class="{
                'el-icon-caret-top': true,
                'sort-active': sortParameter.isNew === 1,
              }"
            ></i>
          </div>
          <div class="sort-icon sort-icon-down">
            <i
              :class="{
                'el-icon-caret-bottom': true,
                'sort-active': sortParameter.isNew === 2,
              }"
            ></i>
          </div>
        </div>
      </li>
    </ul>
    <div v-if="searchShow" class="search-content">
      <el-input
        :placeholder="$t('message.home.storeSeach')"
        v-model="searchKey"
        @input="inputHandle"
      >
        <i slot="prefix" class="el-input__icon el-icon-search"></i>
      </el-input>
    </div>
  </div>
</template>

<script>
  import { cloneDeep, debounce } from "lodash";
  import { EventBus } from "../../event-bus";
  export default {
    name: "EsSort",
    props: {
      priceSort: {
        type: String,
        default: "",
      },
      salesSort: {
        type: String,
        default: "",
      },
      newSort: {
        type: String,
        default: "",
      },
      isRenew: {
        type: Boolean,
        default: false,
      },
      searchShow: {
        type: Boolean,
        default: false,
      },
      hideNew: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        sortParameter: {
          isPrice: 0,
          isNew: 0,
          isRec: 0,
          isHot: 0,
        },
        currentType: "complex",
        searchKey: "",
        itemname: process.env.VUE_APP_ITEM_NAME,
      };
    },
    mounted(){
      if(this.itemname === 'Argos' || this.itemname === 'INT Overstock'){
        this.sortEvent('isHot', 2)
      }
    },
    methods: {
      inputHandle: debounce(function () {
        this.$emit("search", this.searchKey);
      }, 500),
      sortEvent(type, order) {
        this.currentType = type;
        const originData = {
          isPrice: 0,
          isNew: 0,
          isRec: 0,
          isHot: 0,
        };

        if (type === "complex") {
          this.sortParameter = cloneDeep(originData);
        } else {
          if (order) {
            // 如果有入参 改变排序方式
            this.$set(this.sortParameter, type, order);
          } else {
            if (this.sortParameter[type]) {
              this.sortParameter[type]++;
              if (this.sortParameter[type] > 2) this.sortParameter[type] = 0;
            } else {
              this.sortParameter = cloneDeep(originData);
            }
          }
          // console.log("this.sortParameter ->", this.sortParameter);
          EventBus.$emit("sort", this.sortParameter);
        }

        /**
         * 排序不可多个一起，需改成单个排序
         */
        const newSortParams = {};
        Object.keys(this.sortParameter).forEach((key) => {
          if (
            key !== type &&
            ["isPrice", "isNew", "isRec", "isHot"].includes(key)
          ) {
            this.sortParameter[key] = 0;
          } else {
            newSortParams[key] = this.sortParameter[key];
          }
        });
        this.$emit("sort", type === "complex" ? {} : newSortParams);
      },
    },
  };
</script>

<style lang="scss">
  .commodity-content-title {
    color: var(--color-black);
    padding: 22px 28px 0 28px;
    user-select: none;
    position: relative;

    .search-content {
      position: absolute;
      right: -3px;
      .el-input__inner {
        border-radius: 40px;
      }
    }

    h2 {
      font-weight: 500;
      font-size: 14px;
      color: var(--color-black);
      margin-right: 43px;
    }
    .checked {
      color: red;
    }
    ul {
      margin-left: 0;
    }

    li {
      margin-right: 46px;
      cursor: pointer;

      span {
        font-weight: 500;
        font-size: 14px;
        margin-right: 5px;
      }

      > div {
        flex-direction: column;
      }
    }

    .el-icon-caret-top {
      margin-bottom: -8px;
      font-size: 14px;
    }

    .el-icon-caret-bottom {
      font-size: 14px;
    }

    .sort-icon {
      height: 10px;
      position: relative;
      width: 14px;

      i {
        color: #d9d9d9;
        position: absolute;
      }

      .sort-active {
        color: var(--color-main);
      }
    }

    .sort-icon-up {
      i {
        bottom: 4px;
      }
    }

    .sort-icon-down {
      i {
        top: -4px;
      }
    }
  }
</style>
