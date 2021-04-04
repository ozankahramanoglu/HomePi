package com.example.demo.Controllers;

import com.example.demo.Entities.Status;
import com.example.demo.Repositories.StatusRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class StatusController {

    public StatusController(StatusRepository repository) {
        this.repository = repository;
    }

    private final StatusRepository repository;

    @GetMapping("/getStatus/{id}")
    public String getStatusText(@PathVariable Integer id){
        Status status =repository.findById(id).orElseThrow(()-> new RuntimeException("placeholder"));
        return status.getStatus();
    }
    @GetMapping("/getAllStatus")
    public List<Status> getAllStatus(){
        List<Status> status =repository.findAll();
        return status;
    }
}
