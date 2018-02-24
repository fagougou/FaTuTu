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

  var targetDir = './'
  var form = new multiparty.Form({
    "uploadDir": './'
  });
  form.parse(req, function (err, fields, files) {
    if (err) {
      
      return res.status(500).send({ errcode: "500", msg: err })
    }
    try {
      var originalFile = files.file[0].originalFilename
      fs.renameSync(files.file[0].path, originalFile);
      console.log(originalFile)
      res.send({ status: 'ok' })
    } catch (e) {
      console.log(e)
      res.status(500).send({ errcode: "500", msg: e })
    }

  })
})

//获取已上传图片
router.get('/imgs', (req, res, next) => {

})

module.exports = router;
