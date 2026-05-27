<template>
  <div v-if="!item.hidden&&!(item.unShowMenu&&item.unShowMenu.length>0)">
    <template
        v-if="hasOneShowingChild(item.children,item) && (!onlyOneChild.children||onlyOneChild.noShowingChildren)">
      <app-link
          v-if="onlyOneChild.meta&&!onlyOneChild.meta.unShow"
          :to="resolvePath(onlyOneChild.path)">
        <el-tooltip effect="light" :hide-after="0" :content="$t(onlyOneChild.meta.title)" placement="right">
          <el-menu-item :class="{'submenu-title-noDropdown':!isNest}" :index="resolvePath(onlyOneChild.path)">
            <i v-if="(onlyOneChild.meta.icon||'').includes('el-icon')"
               :class="[onlyOneChild.meta.icon, 'sub-el-icon']"/>
            <svg-icon v-else :icon-class="onlyOneChild.meta.icon"/>
            <span slot='title' class="sidebar-text">{{ $t(onlyOneChild.meta.title) }}</span>
          </el-menu-item>
        </el-tooltip>
      </app-link>
    </template>
    <el-submenu v-else ref="subMenu" :index="resolvePath(item.path)" popper-append-to-body menu-trigger="click">
      <el-tooltip effect="light" :content="$t(item.meta.title)" placement="right" slot="title">
        <div>
          <i v-if="(item.meta.icon||'').includes('el-icon')" :class="[item.meta.icon, 'sub-el-icon']"/>
          <svg-icon v-else :icon-class="item.meta.icon"/>
          <span class="sidebar-text">{{ $t(item.meta.title) }}</span>
        </div>
      </el-tooltip>
      <el-tooltip v-for="child in item.children" :key="child.path" effect="light" :content="$t(child.meta.title)"
                  placement="right">
        <sidebar-item :base-path="resolvePath(child.path)"
                      :is-nest="true"
                      :item="child" class="nest-menu"/>
      </el-tooltip>
    </el-submenu>
  </div>
</template>

<script>
import path from 'path'
import {isExternal} from '@/utils/validate'
import AppLink from './Link'
import FixiOSBug from './FixiOSBug'
import settings from "@/settings";

export default {
  name: 'SidebarItem',
  components: {AppLink},
  mixins: [FixiOSBug],
  props: {
    // route object
    item: {
      type: Object,
      required: true
    },
    isNest: {
      type: Boolean,
      default: false
    },
    basePath: {
      type: String,
      default: ''
    }
  },
  data() {
    // To fix https://github.com/PanJiaChen/vue-admin-template/issues/237
    // TODO: refactor with render function
    this.onlyOneChild = null
    return {
      settings,
    }
  },
  methods: {
    hasOneShowingChild(children = [], parent) {
      const showingChildren = children.filter(item => {
        if (item.hidden) {
          return false
        } else {
          // Temp set(will be used if only has one showing child)
          this.onlyOneChild = item
          return true
        }
      })

      // When there is only one child router, the child router is displayed by default
      if (showingChildren.length === 1) {
        return true
      }

      // Show parent if there are no child router to display
      if (showingChildren.length === 0) {
        this.onlyOneChild = {...parent, path: '', noShowingChildren: true}
        return true
      }

      return false
    },
    resolvePath(routePath) {
      if (isExternal(routePath)) {
        return routePath
      }
      if (isExternal(this.basePath)) {
        return this.basePath
      }
      return path.resolve(this.basePath, routePath)
    }
  }
}
</script>

<style lang="scss">
.sidebar-container .sub-el-icon {
  position: relative;
  left: -3px;
}

.el-menu::-webkit-scrollbar {
  /*隐藏滚轮*/
  display: none;
}

.sidebar-text {
  //  超出隐藏显示...
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 120px;
  display: inline-block;
  padding-left: 6px;
}

.el-tooltip__popper.is-light {
  border: solid 1px #e5e5e5 !important;
  color: #333333;
}

.el-tooltip__popper.is-light[x-placement^=right] .popper__arrow {
  border-right-color: #e5e5e5 !important;
}
</style>
