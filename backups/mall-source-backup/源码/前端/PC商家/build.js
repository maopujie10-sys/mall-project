const {execSync} = require('child_process');
const fs = require('fs');
const path = require('path');
const archiver = require('archiver');

// 获取待打包的应用程序列表
async function getBuildList() {
    const packageJson = require('./package.json');
    return Object.keys(packageJson.scripts).filter(script => script.startsWith('build:'));
}

// 执行打包命令
function runBuildCommand(command) {
    execSync(command, {encoding: 'utf-8'});
}

// 重命名dist目录
function renameDistDir(dirName) {
    const srcPath = path.join(__dirname, 'dist');
    const destPath = path.join(__dirname, `商户PC_${dirName.replace(/build:/g, '')}`); // Remove "build:"

    fs.renameSync(srcPath, destPath);
    console.log(`重命名dist目录完成：商户PC_${dirName.replace(/build:/g, '')}`);
}

// 压缩打包文件
function zipBuildFolder(dirName) {
    const srcPath = path.join(__dirname, `商户PC_${dirName.replace(/build:/g, '')}`);
    const destPath = path.join(__dirname, 'buildFiles', `商户PC_${dirName.replace(/build:/g, '')}.zip`);

    const output = fs.createWriteStream(destPath);
    const archive = archiver('zip', {zlib: {level: 9}});

    output.on('close', function () {
        console.log(`压缩完成：商户PC_${dirName.replace(/build:/g, '')}.zip`);
        deleteFolderRecursive(srcPath);
    });

    archive.on('error', function (err) {
        throw err;
    });

    archive.pipe(output);
    archive.directory(srcPath, false);
    archive.finalize();
}


// 删除文件夹
function deleteFolderRecursive(folderPath) {
    if (fs.existsSync(folderPath)) {
        fs.readdirSync(folderPath).forEach(function (file) {
            const curPath = path.join(folderPath, file);
            if (fs.lstatSync(curPath).isDirectory()) {
                deleteFolderRecursive(curPath);
            } else {
                fs.unlinkSync(curPath);
            }
        });
        fs.rmdirSync(folderPath);
    }
}

// 删除目录中的所有文件
function clearDirectory(directoryPath) {
    if (fs.existsSync(directoryPath)) {
        fs.readdirSync(directoryPath).forEach(function (file) {
            const curPath = path.join(directoryPath, file);
            if (fs.lstatSync(curPath).isDirectory()) { // 如果是目录则递归删除
                deleteFolderRecursive(curPath);
            } else { // 删除文件
                fs.unlinkSync(curPath);
            }
        });
    }
}

// 执行打包列表
async function executeBuildList() {
    if (!fs.existsSync(path.join(__dirname, 'buildFiles'))) {
        fs.mkdirSync(path.join(__dirname, 'buildFiles'));
    } else {
        clearDirectory(path.join(__dirname, 'buildFiles')); // 清空buildFiles目录
    }

    // 获取待打包的应用程序列表
    const buildList = await getBuildList();

    for (const buildCommand of buildList) {
        runBuildCommand(`npm run ${buildCommand}`);
        renameDistDir(buildCommand);
        zipBuildFolder(buildCommand);
    }

    console.log('所有打包命令执行完毕');
}

executeBuildList();
