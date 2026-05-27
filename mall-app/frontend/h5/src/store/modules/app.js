const getStorgeSearchData = () => {
  const storgeData = localStorage.getItem('searchHistory')
  return (storgeData && storgeData.length) ? JSON.parse(storgeData) : []
}

const hasInArr = (arr, val) => {
  if (arr.length) {
    for (let i = 0; i < arr.length; i++) {
      if (arr[i].goodsId === val.goodsId) {
        return true
      }
    }
    return false
  } else {
    return false
  }
}

export default {
  state: {
    searchHistory: []
  },
  getters: {
    searchHistory: (state) => {
      return state.searchHistory.length ? state.searchHistory : getStorgeSearchData()
    }
  },
  mutations: {
    SET_SEARCH_HISTORY: (state, arr) => {
      const arrStr = JSON.stringify(arr)
      state.searchHistory = arr
      localStorage.setItem('searchHistory', arrStr)
    },
    CLEAR_SEARCH_HISTORY: (state) => {
      state.searchHistory = []
      localStorage.removeItem('searchHistory')
    }
  },
  actions: {
    setSearchHistory: ({commit, state}, val) => {
      const storeData = state.searchHistory.length ? state.searchHistory : getStorgeSearchData()
      const data = [...storeData]
      if (!hasInArr(storeData, val)) {
        data.push(val)
      }
      commit('SET_SEARCH_HISTORY', data)
    },
    clearSearchHistory: ({commit}) => {
      commit('CLEAR_SEARCH_HISTORY')
    }
  }
}
