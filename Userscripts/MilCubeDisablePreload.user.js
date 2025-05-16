// ==UserScript==
// @name         MilCubeDisablePreload
// @namespace    http://tampermonkey.net/
// @version      0.1
// @author       eWloYW8
// @description  去除百万立方网页的预加载动画
// @match        *://milcubes.zju.edu.cn/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    
    console.log("Tampermonkey script MilCubeDisablePreload loaded!");

    document.getElementById('page-preloader').remove()
})();
