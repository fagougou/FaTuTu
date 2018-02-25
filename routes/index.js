var express = require('express');
var router = express.Router();
var fs = require('fs')
var multiparty = require('multiparty');

/* GET home page. */
router.get('/', function (req, res, next) {
  res.render('index', { title: 'Express' });
});

//上传图片
router.post('/upload', (req, res, next) => {

  var targetDir = './public/userImg/'
  var form = new multiparty.Form({
    "uploadDir": './public/userImg'
  });
  form.parse(req, function (err, fields, files) {
    if (err) {
      console.log(err)
      
      return res.status(500).send({ errcode: "500", msg: err })
    }
    try {
      var originalFile = targetDir + files.file[0].originalFilename
      fs.renameSync(files.file[0].path, originalFile);
      console.log(originalFile)
      res.send({ status: 'ok' })
    } catch (e) {
      console.log(e)
      res.status(500).send({ errcode: "500", msg: e })
    }

  })
})

let  join = require('path').join;
function findSync(startPath) {
    let result=[];
    function finder(path) {
        let files=fs.readdirSync(path);
        files.forEach((val,index) => {
            let fPath=join(path,val);
            let stats=fs.statSync(fPath);
            if(stats.isDirectory()) finder(fPath);
            if(stats.isFile()) result.push(fPath);
        });

    }
    finder(startPath);
    return result;
}


//获取已上传图片
router.get('/imgs', (req, res, next) => {
  let fileNames=findSync('./public/userImg');
  res.send({
    data:fileNames
  })
})

module.exports = router;
