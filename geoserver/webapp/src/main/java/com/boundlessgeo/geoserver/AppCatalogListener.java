/* (c) 2014 Boundless, http://boundlessgeo.com
 * This code is licensed under the GPL 2.0 license.
 */
package com.boundlessgeo.geoserver;

import org.geoserver.catalog.Catalog;
import org.geoserver.catalog.CatalogException;
import org.geoserver.catalog.event.CatalogAddEvent;
import org.geoserver.catalog.event.CatalogEvent;
import org.geoserver.catalog.event.CatalogListener;
import org.geoserver.catalog.event.CatalogModifyEvent;
import org.geoserver.catalog.event.CatalogPostModifyEvent;
import org.geoserver.catalog.event.CatalogRemoveEvent;

/**
 * Example AppCatalogListener - if making changes to catalog objects ensure that
 * the listener is not reentrant. This is easy enough using a boolean flag (see modifying).
 * The CatalogListener should not be accessed by multiple threads so this naive
 * approach _should_work
 */
public class AppCatalogListener implements CatalogListener {
    private final Catalog catalog;
    boolean modifying = false;

    void log(CatalogEvent ev) {
        System.out.println(ev.getClass() + " : " + ev.getSource());
    }

    public AppCatalogListener(Catalog catalog) {
        this.catalog = catalog;
        catalog.addListener(this);
    }

    @Override
    public void handleAddEvent(CatalogAddEvent event) throws CatalogException {
        log(event);
        if (true && !modifying) { // some condition
            // do something else with another catalog object
            try {
                modifying = true;
                // modify another object
            } finally {
                modifying = false;
            }
        }
    }

    @Override
    public void handleModifyEvent(CatalogModifyEvent event) throws CatalogException {
        log(event);
    }

    @Override
    public void handlePostModifyEvent(CatalogPostModifyEvent event) throws CatalogException {
        log(event);
    }

    @Override
    public void handleRemoveEvent(CatalogRemoveEvent event) throws CatalogException {
        log(event);
    }

    @Override
    public void reloaded() {
    }

}
