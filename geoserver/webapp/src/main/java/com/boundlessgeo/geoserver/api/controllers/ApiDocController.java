package com.boundlessgeo.geoserver.api.controllers;

import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Controller;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

@Controller
@RequestMapping("/api")
public class ApiDocController {
    /**
     * Static list of users to simulate Database
     */
    private static List<String> userList = new ArrayList<String>();

    //Initialize the list with some data for index screen
    static {
        userList.add("Billy");
        userList.add("Bob");
    }

    /**
     * Saves the static list of users in model and renders it
     * via freemarker template.
     *
     * @param model
     * @return The index view (FTL)
     */
    @RequestMapping(method = RequestMethod.GET)
    public String index(@ModelAttribute("model") ModelMap model) {

        model.addAttribute("userList", userList);

        return "api-index";
    }

}