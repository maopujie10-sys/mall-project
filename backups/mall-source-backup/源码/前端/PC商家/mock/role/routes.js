// Just a mock data

const constantRoutes = [
  {
    path: '/redirect',
    component: () => import('@/layout'),
    hidden: true,
    children: [
      {
        path: '/redirect/:path*',
        component: () => import('@/views/redirect/index')
      }
    ]
  },
  {
    path: '/login',
    component: () => import('@/views/login/login'),
    hidden: true
  },
  {
    path: '/auth-redirect',
    component: () => import('@/views/login/auth-redirect'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/error-page/404'),
    hidden: true
  },
  {
    path: '/401',
    component: () => import('@/views/error-page/401'),
    hidden: true
  },
  {
    path: '',
    component: () => import('@/layout'),
    redirect: 'dashboard',
    children: [
      {
        path: 'dashboard',
        component: () => import('@/views/dashboard/index'),
        name: 'Dashboard',
        meta: {title: 'Dashboard', icon: 'dashboard', affix: true}
      }
    ]
  },
  {
    path: '/documentation',
    component: () => import('@/layout'),
    children: [
      {
        path: 'index',
        component: () => import('@/views/documentation/index'),
        name: 'Documentation',
        meta: {title: 'Documentation', icon: 'documentation', affix: true}
      }
    ]
  },
  {
    path: '/guide',
    component: () => import('@/layout'),
    redirect: '/guide/index',
    children: [
      {
        path: 'index',
        component: () => import('@/views/guide/index'),
        name: 'Guide',
        meta: {title: 'Guide', icon: 'guide', noCache: true}
      }
    ]
  }
]

const asyncRoutes = [
  {
    path: '/permission',
    component: () => import('@/layout'),
    redirect: '/permission/index',
    alwaysShow: true,
    meta: {
      title: 'Permission',
      icon: 'lock',
      roles: ['admin', 'editor']
    },
    children: [
      {
        path: 'page',
        component: () => import('@/views/permission/page'),
        name: 'PagePermission',
        meta: {
          title: 'Page Permission',
          roles: ['admin']
        }
      },
      {
        path: 'directive',
        component: () => import('@/views/permission/directive'),
        name: 'DirectivePermission',
        meta: {
          title: 'Directive Permission'
        }
      },
      {
        path: 'role',
        component: () => import('@/views/permission/role'),
        name: 'RolePermission',
        meta: {
          title: 'Role Permission',
          roles: ['admin']
        }
      }
    ]
  },

  {
    path: '/icon',
    component: () => import('@/layout'),
    children: [
      {
        path: 'index',
        component: () => import('@/views/icons/index'),
        name: 'Icons',
        meta: {title: 'Icons', icon: 'icon', noCache: true}
      }
    ]
  },

  {
    path: '/components',
    component: () => import('@/layout'),
    redirect: 'noRedirect',
    name: 'ComponentDemo',
    meta: {
      title: 'Components',
      icon: 'component'
    },
    children: [
      {
        path: 'tinymce',
        component: () => import('@/views/components-demo/tinymce'),
        name: 'TinymceDemo',
        meta: {title: 'Tinymce'}
      },
      {
        path: 'markdown',
        component: () => import('@/views/components-demo/markdown'),
        name: 'MarkdownDemo',
        meta: {title: 'Markdown'}
      },
      {
        path: 'json-editor',
        component: () => import('@/views/components-demo/json-editor'),
        name: 'JsonEditorDemo',
        meta: {title: 'Json Editor'}
      },
      {
        path: 'split-pane',
        component: () => import('@/views/components-demo/split-pane'),
        name: 'SplitpaneDemo',
        meta: {title: 'SplitPane'}
      },
      {
        path: 'avatar-upload',
        component: () => import('@/views/components-demo/avatar-upload'),
        name: 'AvatarUploadDemo',
        meta: {title: 'Avatar Upload'}
      },
      {
        path: 'dropzone',
        component: () => import('@/views/components-demo/dropzone'),
        name: 'DropzoneDemo',
        meta: {title: 'Dropzone'}
      },
      {
        path: 'sticky',
        component: () => import('@/views/components-demo/sticky'),
        name: 'StickyDemo',
        meta: {title: 'Sticky'}
      },
      {
        path: 'count-to',
        component: () => import('@/views/components-demo/count-to'),
        name: 'CountToDemo',
        meta: {title: 'Count To'}
      },
      {
        path: 'mixin',
        component: () => import('@/views/components-demo/mixin'),
        name: 'ComponentMixinDemo',
        meta: {title: 'componentMixin'}
      },
      {
        path: 'back-to-top',
        component: () => import('@/views/components-demo/back-to-top'),
        name: 'BackToTopDemo',
        meta: {title: 'Back To Top'}
      },
      {
        path: 'drag-dialog',
        component: () => import('@/views/components-demo/drag-dialog'),
        name: 'DragDialogDemo',
        meta: {title: 'Drag Dialog'}
      },
      {
        path: 'drag-select',
        component: () => import('@/views/components-demo/drag-select'),
        name: 'DragSelectDemo',
        meta: {title: 'Drag Select'}
      },
      {
        path: 'dnd-list',
        component: () => import('@/views/components-demo/dnd-list'),
        name: 'DndListDemo',
        meta: {title: 'Dnd List'}
      },
      {
        path: 'drag-kanban',
        component: () => import('@/views/components-demo/drag-kanban'),
        name: 'DragKanbanDemo',
        meta: {title: 'Drag Kanban'}
      }
    ]
  },
  {
    path: '/charts',
    component: () => import('@/layout'),
    redirect: 'noRedirect',
    name: 'Charts',
    meta: {
      title: 'Charts',
      icon: 'chart'
    },
    children: [
      {
        path: 'keyboard',
        component: () => import('@/views/charts/keyboard'),
        name: 'KeyboardChart',
        meta: {title: 'Keyboard Chart', noCache: true}
      },
      {
        path: 'line',
        component: () => import('@/views/charts/line'),
        name: 'LineChart',
        meta: {title: 'Line Chart', noCache: true}
      },
      // {
      //   path: 'mixchart',
      //   component: () => import('@/views/charts/mixChart'),
      //   name: 'MixChart',
      //   meta: {title: 'Mix Chart', noCache: true}
      // }
    ]
  },
  {
    path: '/nested',
    component: () => import('@/layout'),
    redirect: '/nested/menu1/menu1-1',
    name: 'Nested',
    meta: {
      title: 'Nested',
      icon: 'nested'
    },
    children: [
      {
        path: 'menu1',
        component: () => import('@/views/nested/menu1/index'),
        name: 'Menu1',
        meta: {title: 'Menu1'},
        redirect: '/nested/menu1/menu1-1',
        children: [
          {
            path: 'menu1-1',
            component: () => import('@/views/nested/menu1/menu1-1'),
            name: 'Menu1-1',
            meta: {title: 'Menu1-1'}
          },
          {
            path: 'menu1-2',
            component: () => import('@/views/nested/menu1/menu1-2'),
            name: 'Menu1-2',
            redirect: '/nested/menu1/menu1-2/menu1-2-1',
            meta: {title: 'Menu1-2'},
            children: [
              {
                path: 'menu1-2-1',
                component: () => import('@/views/nested/menu1/menu1-2/menu1-2-1'),
                name: 'Menu1-2-1',
                meta: {title: 'Menu1-2-1'}
              },
              {
                path: 'menu1-2-2',
                component: () => import('@/views/nested/menu1/menu1-2/menu1-2-2'),
                name: 'Menu1-2-2',
                meta: {title: 'Menu1-2-2'}
              }
            ]
          },
          {
            path: 'menu1-3',
            component: () => import('@/views/nested/menu1/menu1-3'),
            name: 'Menu1-3',
            meta: {title: 'Menu1-3'}
          }
        ]
      },
      {
        path: 'menu2',
        name: 'Menu2',
        component: () => import('@/views/nested/menu2/index'),
        meta: {title: 'Menu2'}
      }
    ]
  },

  {
    path: '/example',
    component: () => import('@/layout'),
    redirect: '/example/list',
    name: 'Example',
    meta: {
      title: 'Example',
      icon: 'example'
    },
    children: [
      {
        path: 'create',
        component: () => import('@/views/example/create'),
        name: 'CreateArticle',
        meta: {title: 'Create Article', icon: 'edit'}
      },
      {
        path: 'edit/:id(\\d+)',
        component: () => import('@/views/example/edit'),
        name: 'EditArticle',
        meta: {title: 'Edit Article', noCache: true},
        hidden: true
      },
      {
        path: 'list',
        component: () => import('@/views/example/list'),
        name: 'ArticleList',
        meta: {title: 'Article List', icon: 'list'}
      }
    ]
  },

  {
    path: '/tab',
    component: () => import('@/layout'),
    children: [
      {
        path: 'index',
        component: () => import('@/views/tab/index'),
        name: 'Tab',
        meta: {title: 'Tab', icon: 'tab'}
      }
    ]
  },

  {
    path: '/error',
    component: () => import('@/layout'),
    redirect: 'noRedirect',
    name: 'ErrorPages',
    meta: {
      title: 'Error Pages',
      icon: '404'
    },
    children: [
      {
        path: '401',
        component: () => import('@/views/error-page/401'),
        name: 'Page401',
        meta: {title: 'Page 401', noCache: true}
      },
      {
        path: '404',
        component: () => import('@/views/error-page/404'),
        name: 'Page404',
        meta: {title: 'Page 404', noCache: true}
      }
    ]
  },

  {
    path: '/error-log',
    component: () => import('@/layout'),
    redirect: 'noRedirect',
    children: [
      {
        path: 'log',
        component: () => import('@/views/error-log/index'),
        name: 'ErrorLog',
        meta: {title: 'Error Log', icon: 'bug'}
      }
    ]
  },

  {
    path: '/excel',
    component: () => import('@/layout'),
    redirect: '/excel/export-excel',
    name: 'Excel',
    meta: {
      title: 'Excel',
      icon: 'excel'
    },
    children: [
      {
        path: 'export-excel',
        component: () => import('@/views/excel/export-excel'),
        name: 'ExportExcel',
        meta: {title: 'Export Excel'}
      },
      {
        path: 'export-selected-excel',
        component: () => import('@/views/excel/select-excel'),
        name: 'SelectExcel',
        meta: {title: 'Select Excel'}
      },
      {
        path: 'export-merge-header',
        component: () => import('@/views/excel/merge-header'),
        name: 'MergeHeader',
        meta: {title: 'Merge Header'}
      },
      {
        path: 'upload-excel',
        component: () => import('@/views/excel/upload-excel'),
        name: 'UploadExcel',
        meta: {title: 'Upload Excel'}
      }
    ]
  },

  {
    path: '/zip',
    component: () => import('@/layout'),
    redirect: '/zip/download',
    alwaysShow: true,
    meta: {title: 'Zip', icon: 'zip'},
    children: [
      {
        path: 'download',
        component: () => import('@/views/zip/index'),
        name: 'ExportZip',
        meta: {title: 'Export Zip'}
      }
    ]
  },

  {
    path: '/pdf',
    component: () => import('@/layout'),
    redirect: '/pdf/index',
    children: [
      {
        path: 'index',
        component: () => import('@/views/pdf/index'),
        name: 'PDF',
        meta: {title: 'PDF', icon: 'pdf'}
      }
    ]
  },
  {
    path: '/pdf/download',
    component: () => import('@/views/pdf/download'),
    hidden: true
  },

  {
    path: '/theme',
    component: () => import('@/layout'),
    redirect: 'noRedirect',
    children: [
      {
        path: 'index',
        component: () => import('@/views/theme/index'),
        name: 'Theme',
        meta: {title: 'Theme', icon: 'theme'}
      }
    ]
  },

  {
    path: '/clipboard',
    component: () => import('@/layout'),
    redirect: 'noRedirect',
    children: [
      {
        path: 'index',
        component: () => import('@/views/clipboard/index'),
        name: 'ClipboardDemo',
        meta: {title: 'Clipboard Demo', icon: 'clipboard'}
      }
    ]
  },

  // {
  //   path: '/i18n',
  //   component: () => import('@/layout'),
  //   children: [
  //     {
  //       path: 'index',
  //       component: () => import('@/views/i18n-demo/index'),
  //       name: 'I18n',
  //       meta: {title: 'I18n', icon: 'international'}
  //     }
  //   ]
  // },

  {
    path: 'external-link',
    component: () => import('@/layout'),
    children: [
      {
        path: 'https://github.com/PanJiaChen/vue-element-admin',
        meta: {title: 'External Link', icon: 'link'}
      }
    ]
  },
  {path: '*', redirect: '/404', hidden: true}
]

module.exports = {
  constantRoutes,
  asyncRoutes
}
