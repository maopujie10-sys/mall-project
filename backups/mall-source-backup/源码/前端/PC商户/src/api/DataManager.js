import Axios from '../util/http'


function ApiFun(apiid,param, cb,tthis) {

    Axios.fetch(apiid,param)
      .then((res) => {

        cb(res,tthis);
      })
      .catch((err) => {
        console.log(err);
      });

  }
  export default{
    ApiFun
} 